package com.geeks4learning.CourseGen.Controller;

import com.geeks4learning.CourseGen.Model.ChatCompletionRequest;
import com.geeks4learning.CourseGen.Model.ChatCompletionResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
public class AIController {

    @Autowired
    private RestTemplate restTemplate;

    @Value("${openai.completions}")
    private String completionsURL;

    @PostMapping("/generateCourse")
    public String promptHandler(@RequestBody String prompt) {
        String valueAddedPrompt = "Please generate a course outline for a book teaching about: ";
        valueAddedPrompt += prompt;

        // Generate outline
        String outline = respondToPrompt(valueAddedPrompt);

        // Split the outline into sections to request content for each unit
        String detailedContent = generateDetailedContentForOutline(outline);

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
            String sectionPrompt = "Please provide detailed content for the section: " + section;
            String sectionContent = respondToPrompt(sectionPrompt);

            // Append section and its content
            detailedContentBuilder.append("Section: ").append(section).append("\n");
            detailedContentBuilder.append(sectionContent).append("\n\n");
        }

        return detailedContentBuilder.toString();
    }
    // N.B for now the system outputs the first outline and there after outputs a
    // textbook that has the same outline and added content
}
