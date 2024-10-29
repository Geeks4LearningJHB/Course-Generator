package com.geeks4learning.CourseGen.Controller;

import com.geeks4learning.CourseGen.Model.ChatCompletionRequest;
import com.geeks4learning.CourseGen.Model.ChatCompletionResponse;
import com.geeks4learning.CourseGen.Services.AdminService;

import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.apache.poi.xwpf.usermodel.XWPFRun;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import java.io.FileOutputStream;
import java.io.IOException;

@RestController
public class AIController {

    @Autowired
    private RestTemplate restTemplate;

    @Value("${openai.completions}")
    private String completionsURL;

    @PostMapping("/generateCourse")
    public String promptHandler(@RequestBody String prompt) {
        String valueAddedPrompt = "Please generate a detailed course outline for a textbook teaching about: " + prompt +
                ". The outline should be organized as a Module. A Module should contain several Units. " +
                "Each Unit should include topics covered, suggested activities, and an assessment.";
        ;

        // Generate outline
        String outline = respondToPrompt(valueAddedPrompt);

        // Split the outline into sections to request content for each unit
        String detailedContent = generateDetailedContentForOutline(outline);
        exportToWord(detailedContent, "CourseOutline.docx");

        return detailedContent;
    }

    private String respondToPrompt(String prompt) {
        ChatCompletionRequest chatCompletionRequest = new ChatCompletionRequest("gpt-4o-mini", prompt);
        ChatCompletionResponse chatCompletionResponse = restTemplate.postForObject(completionsURL,
                chatCompletionRequest,
                ChatCompletionResponse.class);
        assert chatCompletionResponse != null;

        String strResponse = chatCompletionResponse.getChoices().get(0).getMessage().getContent();
        return strResponse;
    }

    private String generateDetailedContentForOutline(String outline) {
        StringBuilder detailedContentBuilder = new StringBuilder();

        String[] sections = outline.split("\n");
        for (String section : sections) {
            // Skip empty lines or irrelevant sections
            if (section.trim().isEmpty()) {
                continue;
            }

            // Generate content for each section
            String sectionPrompt = "Please provide detailed content for the Unit titled: " + section;
            String sectionContent = respondToPrompt(sectionPrompt);

            // Append section and its content
            detailedContentBuilder.append("Section: ").append(section).append("\n");
            detailedContentBuilder.append(sectionContent).append("\n\n");
        }

        return detailedContentBuilder.toString();
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
