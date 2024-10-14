package com.geeks4learning.courseGenerator.Controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.util.JSONPObject;
import com.geeks4learning.courseGenerator.Model.ChatCompletionRequest;
import com.geeks4learning.courseGenerator.Model.ChatCompletionResponse;
import org.apache.tomcat.util.json.JSONParser;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.jackson.JsonObjectSerializer;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.StringTokenizer;

@RestController
public class MainController {

    @Autowired
    private RestTemplate restTemplate;
    @Value("${openai.completions}")
    private String completionsURL;
    @PostMapping("/generateCourse")
    public String promptHandler(@RequestBody String prompt){
        String valueAddedPrompt = "Please generate an outline for a book about: ";
        valueAddedPrompt += prompt;
        //String refinedPrompt = respondToPrompt(valueAddedPrompt);
        return  respondToPrompt(valueAddedPrompt);
    }

    private String respondToPrompt(String prompt){
        ChatCompletionRequest chatCompletionRequest =
                new ChatCompletionRequest("gpt-4o-mini", prompt);
        ChatCompletionResponse chatCompletionResponse =
                restTemplate.postForObject(completionsURL,
                        chatCompletionRequest,
                        ChatCompletionResponse.class);
        assert chatCompletionResponse != null;

        /*ObjectMapper objectMapper = new ObjectMapper();
        String jsonChatCompletionResponse = "";
        try {
            // Convert object to JSON string
            jsonChatCompletionResponse = objectMapper.writeValueAsString(chatCompletionResponse);

            //System.out.println(jsonString);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        } */

        String strResponse = chatCompletionResponse.getChoices().get(0).getMessage().getContent();

        StringBuilder stringBuilder = new StringBuilder();

        String[] sections = strResponse.split("\n");
        int i = 0;
        for(String section: sections){
            stringBuilder.append(i).append("\n").append(section).append("\n\n");
            i++;
        }

        return  stringBuilder.toString();
    }
}
