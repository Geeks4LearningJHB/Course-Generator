package com.geeks4learning.CourseGen.Controller;

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

    @Value("${openai.api-key}")
    private String apiKey;

    
@PostMapping("/generateCourse")
    public CourseNode promptHandler(@RequestBody CourseRequest courseRequest) {
        return generateCourseTree(
            courseRequest.getCourseTitle(),
            courseRequest.getDifficulty(),
            courseRequest.getDuration()
        );
    }

    private CourseNode generateCourseTree(String courseTitle, String difficulty, int duration) {
        String courseOutlinePrompt = "Please generate a detailed course outline for a textbook teaching about: "
                + courseTitle +
                ". The course should be designed for a " + difficulty
                + " level and is intended to be completed in " + duration + " months. " +
                "The outline should be organized as Modules. Each Module should contain Units with topics, suggested activities, and assessments.";

        String outline = respondToPrompt(courseOutlinePrompt);
        CourseNode root = new CourseNode(courseTitle);

        String[] modules = outline.split("Module");
        for (String module : modules) {
            if (module.trim().isEmpty()) continue;

            CourseNode moduleNode = new CourseNode("Module " + module.trim());
            String moduleDetailsPrompt = "Provide detailed content for " + moduleNode.getTitle();
            String moduleDetails = respondToPrompt(moduleDetailsPrompt);
            moduleNode.setContent(moduleDetails);

            String[] units = moduleDetails.split("Unit");
            for (String unit : units) {
                if (unit.trim().isEmpty()) continue;

                CourseNode unitNode = new CourseNode("Unit " + unit.trim());
                String unitDetailsPrompt = "Provide detailed content for " + unitNode.getTitle();
                String unitDetails = respondToPrompt(unitDetailsPrompt);
                unitNode.setContent(unitDetails);

                moduleNode.addChild(unitNode);
            }

            root.addChild(moduleNode);
        }

        return root;
    }

    private String respondToPrompt(String prompt) {
        ChatCompletionRequest request = new ChatCompletionRequest("gpt-4-mini", prompt);
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + apiKey);
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<ChatCompletionRequest> entity = new HttpEntity<>(request, headers);
        ChatCompletionResponse response = restTemplate.postForObject(completionsURL, entity, ChatCompletionResponse.class);

        if (response != null && !response.getChoices().isEmpty()) {
            return response.getChoices().get(0).getMessage().getContent();
        }

        return "";
    }

















    public void exportToWord(String detailedContent, String fileName) {
        try (XWPFDocument document = new XWPFDocument()) {
            // Create a paragraph in the document
            XWPFParagraph paragraph = document.createParagraph();
            XWPFRun run = paragraph.createRun();
            run.setText(detailedContent);

            // Write the document to the specified file
            try (FileOutputStream out = new FileOutputStream(fileName)) {
                document.write(out);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}
