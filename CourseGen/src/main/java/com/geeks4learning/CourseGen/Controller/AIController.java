package com.geeks4learning.CourseGen.Controller;

import com.geeks4learning.CourseGen.DTOs.CourseModuleDTO;
import com.geeks4learning.CourseGen.DTOs.PromtDTO;
import com.geeks4learning.CourseGen.Entities.Activity;
import com.geeks4learning.CourseGen.Entities.Assessment;
import com.geeks4learning.CourseGen.Entities.CourseModule;
import com.geeks4learning.CourseGen.Entities.Promt;
import com.geeks4learning.CourseGen.Entities.Unit;
import com.geeks4learning.CourseGen.Model.ChatCompletionRequest;
import com.geeks4learning.CourseGen.Model.ChatCompletionResponse;
import com.geeks4learning.CourseGen.Services.ActivityService;
import com.geeks4learning.CourseGen.Services.AssessmentService;
import com.geeks4learning.CourseGen.Services.ModuleService;
import com.geeks4learning.CourseGen.Services.PromptService;
import com.geeks4learning.CourseGen.Services.UnitService;

import jakarta.transaction.Transactional;

import java.util.*;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
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
    public String promptHandler(@RequestBody String prompt, String difficulty, int duration) {
        // Step 1: Save the prompt
        PromtDTO newPrompt = new PromtDTO(prompt, difficulty, duration);
        promptService.savePrompt(newPrompt);

        // Step 2: Generate module (only name, description, and duration)
        String moduleOutlinePrompt = "Please generate a course outline for a book teaching about: " + prompt
                + " that would take " + duration + " long (in months) with a difficulty level of " + difficulty;
        String moduleOutline = respondToPrompt(moduleOutlinePrompt);

        // Parse module details
        CourseModule module = parseModuleOutline(moduleOutline);
        moduleService.saveModule(module);

        // Ensure units list is initialized if it is null
        if (module.getUnits() == null) {
            module.setUnits(new ArrayList<>());
        }


        // Step 3: Generate and save units
        String detailedContent = generateDetailedContentForOutline(moduleOutline);
        for (String unitContent : detailedContent.split("\n\n")) {

        Unit unit = new Unit();

            int chapterNumber = module.getUnits().size() + 1; // Example to generate sequence
            String unitName = "Chapter " + chapterNumber + ": Introduction to " + module.getModuleName();

            unit.setUnitName(unitName); // Set dynamic name for each unit
            unit.setContent(unitContent);
            unit.setModule(module); // Link 'module' (CourseModule instance)
            unitService.saveUnit(unit);
            module.getUnits().add(unit); // Add unit to module’s list of units

            // Step 5: Generate and save activities
            String activityPrompt = "Generate activities related to the module on " + prompt;
            String activityContent = respondToPrompt(activityPrompt);
            Activity activity = new Activity(activityContent, unit); // Now 'unit' is defined
            activityService.saveActivity(activity);
        }

        // // Step 4: Generate and save assessments
        // String assessmentName = "Assessment for " + prompt; // Example name
        // Assessment assessment = new Assessment(assessmentName, duration, unit); // Make sure to pass a Unit object
        // assessmentService.saveAssessment(assessment);

        // // Step 5: Generate and save activities again as part of assessment
        // String activityPrompt = "Generate activities related to the module on " + prompt;
        // String activityContent = respondToPrompt(activityPrompt);
        // Activity activity = new Activity(activityContent, unit); // Replace 'unit' with the actual Unit object
        // activityService.saveActivity(activity);

        return "Module, Units, Assessment, and Activity generated and saved successfully.";
    }

    private String respondToPrompt(String prompt) {
        ChatCompletionRequest chatCompletionRequest = new ChatCompletionRequest("gpt-4o-mini", prompt);
        ChatCompletionResponse chatCompletionResponse = restTemplate.postForObject(
                completionsURL, chatCompletionRequest, ChatCompletionResponse.class);
        assert chatCompletionResponse != null;
        return chatCompletionResponse.getChoices().get(0).getMessage().getContent();
    }

    private String generateDetailedContentForOutline(String outline) {
        StringBuilder detailedContentBuilder = new StringBuilder();

        String[] sections = outline.split("\n");
        for (String section : sections) {
            if (section.trim().isEmpty())
                continue;

            String sectionPrompt = "Please provide detailed content for the section: " + section;
            String sectionContent = respondToPrompt(sectionPrompt);

            detailedContentBuilder.append(section).append(": ").append(sectionContent).append("\n\n");
        }

        return detailedContentBuilder.toString();
    }

    private CourseModule parseModuleOutline(String outline) {
        String[] parts = outline.split("#", 3);
        String name = parts[0].trim();
        String description = parts.length > 1 ? parts[1].trim() : "";
        String duration = parts.length > 2 ? parts[2].trim() : "";
        return new CourseModule(name, description, duration);
    }

    // @GetMapping("/getCourseModuleDetails/{id}")
    // public String getCourseModuleDetails(@PathVariable Long id) {
    //     Optional<CourseModule> optionalModule = moduleService.getModuleById(id);

    //     if (optionalModule.isPresent()) {
    //         CourseModule module = optionalModule.get();
    //         List<Unit> units = unitService.findUnitsByModuleId(id);
    //         List<Assessment> assessments = assessmentService.findAssessmentsByModuleId(id);
    //         List<Activity> activities = activityService.findActivitiesByModuleId(id);

    //         StringBuilder responseBuilder = new StringBuilder();
    //         responseBuilder.append("Course Module:\n").append(module.toString()).append("\n");

    //         responseBuilder.append("\nUnits:\n");
    //         units.forEach(unit -> responseBuilder.append(unit.toString()).append("\n"));

    //         responseBuilder.append("\nAssessments:\n");
    //         assessments.forEach(assessment -> responseBuilder.append(assessment.toString()).append("\n"));

    //         responseBuilder.append("\nActivities:\n");
    //         activities.forEach(activity -> responseBuilder.append(activity.toString()).append("\n"));

    //         return responseBuilder.toString();
    //     } else {
    //         return "Course Module with ID " + id + " not found.";
    //     }
    // }

    @GetMapping("/findModule")
    public List<CourseModuleDTO> findModule(@RequestParam(required = false, defaultValue = "") String search) {
        // Fetch modules based on the search criteria
        List<CourseModule> modules = moduleService.findModuleByName(search);

        // Convert the modules to DTOs
        return moduleService.convertModulesToDTO(modules);
    }

// Helper method to convert to CourseModuleDTO
private CourseModuleDTO convertToDTO(CourseModule module) {
    return new CourseModuleDTO(module.getModuleId(), 
                                module.getModuleName(), 
                                module.getModuleDescription(), 
                                module.getDuration(), 
                                unitService.convertUnitsToDTO(module.getUnits()));
}
    

}
