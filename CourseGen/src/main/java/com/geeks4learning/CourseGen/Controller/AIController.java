package com.geeks4learning.CourseGen.Controller;

import com.geeks4learning.CourseGen.DTOs.CourseNode;
import com.geeks4learning.CourseGen.DTOs.PromtDTO;
import com.geeks4learning.CourseGen.Entities.Activity;
import com.geeks4learning.CourseGen.Entities.Assessment;
import com.geeks4learning.CourseGen.Entities.CourseModule;
import com.geeks4learning.CourseGen.Entities.Promt;
import com.geeks4learning.CourseGen.Entities.Unit;
import com.geeks4learning.CourseGen.Model.ChatCompletionRequest;
import com.geeks4learning.CourseGen.Model.ChatCompletionResponse;
import com.geeks4learning.CourseGen.Model.CourseRequest;
import com.geeks4learning.CourseGen.Services.ActivityService;
import com.geeks4learning.CourseGen.Services.AssessmentService;
import com.geeks4learning.CourseGen.Services.ModuleService;
import com.geeks4learning.CourseGen.Services.PromptService;
import com.geeks4learning.CourseGen.Services.UnitService;

import java.util.*;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
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
 
    @Autowired
    private PromptService promptService;
 
    @Autowired
    private ModuleService moduleService;
 
    @Autowired
    private UnitService unitService;
 
    @Autowired
    private AssessmentService assessmentService;
 
    @Autowired
    private ActivityService activityService;
 
    @Value("${openai.completions}")
    private String completionsURL;
 
    @PostMapping("/generateCourse")
    public ResponseEntity<Map<String, Object>> generateCourse(@RequestBody String prompt, String difficulty,
            int duration) {
        ExecutorService executorService = Executors.newFixedThreadPool(3);
        Map<String, Object> response = new HashMap<>();
        try {
            // Step 1: Generate the prompt and course outline
            PromtDTO newPrompt = new PromtDTO(prompt, difficulty, duration);
            Promt generatedPrompt = promptService.savePrompt(newPrompt); // Still save the prompt if needed
 
            // Generate module outline
            String moduleOutlinePrompt = "Please generate a course outline for a book teaching about: " + prompt
                    + " that would take " + duration + " months with a difficulty level of " + difficulty;
            String moduleOutline = respondToPrompt(moduleOutlinePrompt);
            CourseModule module = parseModuleOutline(moduleOutline); // Parse the generated module
 
            if (module.getUnits() == null) {
                module.setUnits(Collections.synchronizedList(new ArrayList<>()));
            }
 
            // Step 2: Generate units content (but don't save yet)
            String detailedContent = generateDetailedContentForOutline(moduleOutline);
            List<Callable<Void>> unitTasks = new ArrayList<>();
            for (String unitContent : detailedContent.split("\\n\\n")) {
                unitTasks.add(() -> {
                    Unit unit = new Unit();
                    synchronized (module.getUnits()) {
                        int chapterNumber = module.getUnits().size() + 1;
                        String unitName = "Chapter " + chapterNumber + ": Introduction to " + module.getModuleName();
                        unit.setUnitName(unitName);
                        unit.setContent(unitContent);
                        unit.setModule(module);
                        // We don't save the unit yet, we return it as part of the response
                        module.getUnits().add(unit);
                    }
 
                    // Generate activities related to the unit (but don't save yet)
                    String activityPrompt = "Generate activities related to the module on " + prompt;
                    String activityContent = respondToPrompt(activityPrompt);
                    // Activity activity = new Activity(activityContent, unit);
                    // Add activity to unit, but don't save it yet
                    // unit.setActivityUnits(Collections.singletonList(activity)); // Assuming the Activity list is set
                                                                                // here
                    return null;
                });
            }
 
            // Execute unit generation tasks in parallel
            List<Future<Void>> unitFutures = executorService.invokeAll(unitTasks);
            for (Future<Void> future : unitFutures) {
                future.get(); // Ensure each unit task completes
            }
 
            // Step 3: Return the generated data (module, units, activities) to the user
            response.put("module", module);
            response.put("units", module.getUnits());
 
            return ResponseEntity.ok(response); // Return the generated content for review
 
        } catch (InterruptedException | ExecutionException e) {
            Thread.currentThread().interrupt();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("message", "Error during generation: " + e.getMessage()));
        } finally {
            executorService.shutdown();
        }
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
 
            detailedContentBuilder.append("<h2>").append("Section: ").append(section).append("</h2>");
            detailedContentBuilder.append("<p>").append(sectionContent).append("</p>");
 
            // Append section and its content
            // detailedContentBuilder.append("Section: ").append(section).append("\n");
            // detailedContentBuilder.append(sectionContent).append("\n\n");
        }
 
        return detailedContentBuilder.toString();
    }
 
    @PostMapping("/saveGeneratedCourse")
    public ResponseEntity<String> saveGeneratedCourse(@RequestBody Map<String, Object> generatedCourseData) {
        try {
            CourseModule module = (CourseModule) generatedCourseData.get("module");
            List<Unit> units = (List<Unit>) generatedCourseData.get("units");
 
            // Save the module
            moduleService.saveModule(module);
 
            // Save the units
            for (Unit unit : units) {
                unitService.saveUnit(unit);
            }
 
            // Optionally save activities and assessments if required
            for (Unit unit : units) {
                for (Activity activity : unit.getActivityUnits()) {
                    activityService.saveActivity(activity);
                }
                // Save assessment (simplified)
                Assessment assessment = new Assessment();
                assessment.setAssessmentName("Assessment for " + module.getModuleName());
                assessment.setDuration(Integer.parseInt(module.getDuration())); // If `module.getDuration()` is a String
                assessment.setUnit(unit);
 
                assessmentService.saveAssessment(assessment);
            }
 
            return ResponseEntity.ok("Module, Units, Activities, and Assessments saved successfully.");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error while saving generated data: " + e.getMessage());
        }
    }
 
    private CourseModule parseModuleOutline(String moduleOutline) {
        CourseModule courseModule = new CourseModule();
        List<Unit> units = new ArrayList<>();
   
        // Split the module outline into sections by newline
        String[] lines = moduleOutline.split("\n");
   
        // Assume the first line is the module name
        if (lines.length > 0) {
            courseModule.setModuleName(lines[0].trim());
        }
   
        // Iterate through the remaining lines to create units
        for (int i = 1; i < lines.length; i++) {
            String line = lines[i].trim();
            if (!line.isEmpty()) {
                Unit unit = new Unit();
                unit.setUnitName(line); // Assuming Unit has a `unitName` field
                unit.setModule(courseModule); // Set the relationship
                units.add(unit);
            }
        }
   
        // Associate the units with the course module
        courseModule.setUnits(units);
   
        return courseModule;
    }
   
}
 
 