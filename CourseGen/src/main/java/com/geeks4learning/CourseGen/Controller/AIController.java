package com.geeks4learning.CourseGen.Controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.geeks4learning.CourseGen.DTOs.CourseNode;
import com.geeks4learning.CourseGen.Model.ChatCompletionRequest;
import com.geeks4learning.CourseGen.Model.ChatCompletionResponse;
import com.geeks4learning.CourseGen.Model.CourseRequest;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.apache.poi.xwpf.usermodel.XWPFRun;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import java.io.FileOutputStream;
import java.io.IOException;

@RestController
@RequestMapping("/AI")
@CrossOrigin(origins = "http://localhost:4200")
public class AIController {

    @Autowired
    private RestTemplate restTemplate;

    @Value("${openai.completions}")
    private String completionsURL;

    @Value("${openai.key}")
    private String apiKey;

    /**
     * Handles the incoming course generation request and returns the generated course tree.
     */
    @PostMapping("/generateCourse")
    public CourseNode promptHandler(@RequestBody CourseRequest courseRequest) {
        validateRequest(courseRequest);
        return generateCourseTree(
                courseRequest.getCourseTitle(),
                courseRequest.getDifficulty(),
                courseRequest.getDuration());
    }

    /**
     * Validates the incoming request to ensure all fields are present.
     */
    private void validateRequest(CourseRequest courseRequest) {
        if (courseRequest == null || courseRequest.getCourseTitle().isBlank()
                || courseRequest.getDifficulty().isBlank() || courseRequest.getDuration() <= 0) {
            throw new IllegalArgumentException("Invalid course request. Ensure all fields are correctly provided.");
        }
    }

    /**
     * Generates a hierarchical course tree based on the outline and details provided by the AI.
     */
    private CourseNode generateCourseTree(String courseTitle, String difficulty, int duration) {
        String courseOutlinePrompt = generatePrompt(courseTitle, difficulty, duration, "Module");
        String outline = respondToPrompt(courseOutlinePrompt);

        if (!outline.contains("Module")) {
            throw new RuntimeException("Response does not contain the expected 'Module' keyword.");
        }

        CourseNode root = new CourseNode(courseTitle);
        processNodes(outline, "Module", root, "Unit");
        return root;
    }

    /**
     * Generates a prompt string for the AI based on provided parameters.
     */
    private String generatePrompt(String title, String level, int duration, String keyNode) {
        String durationStr = duration + " months";
        return "Generate a detailed course outline for a textbook teaching about: " + title + ". " +
                "This course is tailored for a " + level + " difficulty level and spans " + durationStr + ". " +
                "Ensure the response includes the keyword '" + keyNode + "' and provides detailed units, topics, suggested activities, and assessments.";
    }

    /**
     * Processes content recursively to build a tree structure of course nodes.
     */
    private void processNodes(String content, String nodeType, CourseNode parentNode, String childNodeType) {
        String[] nodes = content.split(nodeType);

        for (String nodeContent : nodes) {
            CourseNode node = createCourseNode(nodeContent.trim(), nodeType);
            if (node != null) {
                if (childNodeType != null) {
                    String childDetailsPrompt = "Provide detailed content for " + node.getTitle() + ".";
                    String childDetails = respondToPrompt(childDetailsPrompt);
                    node.setContent(childDetails);
                    processNodes(childDetails, childNodeType, node, null);
                }
                parentNode.addChild(node);
            }
        }
    }

    /**
     * Creates a course node based on its type and content.
     */
    private CourseNode createCourseNode(String content, String type) {
        if (content == null || content.isBlank()) {
            return null;
        }
        return new CourseNode(type + " " + content);
    }

    /**
     * Sends a prompt to the AI and retrieves the response.
     */
    private String respondToPrompt(String prompt) {
        ChatCompletionRequest request = new ChatCompletionRequest("gpt-4o-mini", prompt);
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + apiKey);
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<ChatCompletionRequest> entity = new HttpEntity<>(request, headers);

        try {
            System.out.println("Sending request: " + new ObjectMapper().writeValueAsString(request));
            ChatCompletionResponse response = restTemplate.postForObject(completionsURL, entity, ChatCompletionResponse.class);

            if (response != null && !response.getChoices().isEmpty()) {
                String content = response.getChoices().get(0).getMessage().getContent();
                if (!content.contains("Module")) {
                    throw new RuntimeException("Response does not contain the expected 'Module' keyword.");
                }
                return content;
            } else {
                throw new RuntimeException("No valid choices returned from OpenAI.");
            }
        } catch (Exception e) {
            System.err.println("Request failed: " + e.getMessage());
            return "Error: Failed to get a valid response.";
        }
    }

    /**
     * Exports content to a Word document.
     */
    public void exportToWord(String detailedContent, String fileName) {
        try (XWPFDocument document = new XWPFDocument()) {
            XWPFParagraph paragraph = document.createParagraph();
            XWPFRun run = paragraph.createRun();
            run.setText(detailedContent);

            try (FileOutputStream out = new FileOutputStream(fileName)) {
                document.write(out);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
