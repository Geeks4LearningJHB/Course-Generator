package com.geeks4learning.CourseGen.Controller;

import com.fasterxml.jackson.databind.ObjectMapper;
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

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;




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
        Map<String, Object> response = new HashMap<>();
        try {
            // Step 1: Save the prompt
            PromtDTO newPrompt = new PromtDTO(prompt, difficulty, duration);
            promptService.savePrompt(newPrompt);

            // Step 2: Generate the course outline
            String moduleOutlinePrompt = "Please generate a course outline for a book teaching about: " + prompt +
                    " that would take " + duration + " months with a difficulty level of " + difficulty;
            String moduleOutline = respondToPrompt(moduleOutlinePrompt);
            CourseModule module = parseModuleOutline(moduleOutline);

            if (module.getUnits() == null) {
                module.setUnits(new ArrayList<>());
            }

            // Step 3: Generate detailed content for each unit
            List<CompletableFuture<Void>> unitTasks = Arrays.stream(moduleOutline.split("\n"))
                    .filter(line -> !line.trim().isEmpty())
                    .map(unitName -> CompletableFuture.runAsync(() -> generateUnitContent(module, unitName, prompt)))
                    .collect(Collectors.toList());

            // Wait for all unit tasks to complete
            CompletableFuture.allOf(unitTasks.toArray(new CompletableFuture[0])).join();

            // Step 4: Return the generated course data
            response.put("module", module);
            response.put("units", module.getUnits());
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("message", "Error during generation: " + e.getMessage()));
        }
    }

    private void generateUnitContent(CourseModule module, String unitName, String prompt) {
        Unit unit = new Unit();
        unit.setUnitName(sanitizeText(unitName));
        unit.setModule(module);
    
        String unitContentPrompt = "Provide detailed content for a textbook chapter titled: '" 
                + sanitizeText(unitName) + "' as part of the course '" + prompt + "'.";
        String unitContent = sanitizeText(respondToPrompt(unitContentPrompt));
        unit.setContent(unitContent);
    
        synchronized (module.getUnits()) {
            module.getUnits().add(unit);
        }
    
        String activityPrompt = "Generate 3 practical activities for the chapter: '" 
                + sanitizeText(unitName) + "' in the course '" + prompt + "'.";
        String activityContent = sanitizeText(respondToPrompt(activityPrompt));
    
        Activity activity = new Activity(activityContent, unit);
        unit.setActivityUnits(Collections.singletonList(activity));
    }
    

    private String respondToPrompt(String prompt) {
        ChatCompletionRequest chatCompletionRequest = new ChatCompletionRequest("gpt-4o-mini", prompt);
        ChatCompletionResponse chatCompletionResponse = restTemplate.postForObject(completionsURL,
                chatCompletionRequest, ChatCompletionResponse.class);
        assert chatCompletionResponse != null;
        String rawContent = chatCompletionResponse.getChoices().get(0).getMessage().getContent();
        return sanitizeText(rawContent);
    }
    

    private CourseModule parseModuleOutline(String moduleOutline) {
        CourseModule courseModule = new CourseModule();
        String[] lines = moduleOutline.split("\n");
    
        // Extract the module name and sanitize it
        courseModule.setModuleName(sanitizeText(lines[0]));
    
        List<Unit> units = Arrays.stream(lines, 1, lines.length)
                .map(String::trim)
                .filter(line -> !line.isEmpty() && !line.equals("---")) // Skip invalid lines
                .map(this::sanitizeText) // Sanitize each unit name
                .map(line -> {
                    Unit unit = new Unit();
                    unit.setUnitName(line);
                    unit.setModule(courseModule);
                    return unit;
                })
                .collect(Collectors.toList());
    
        courseModule.setUnits(units);
        return courseModule;
    }
    

    private String sanitizeText(String text) {
    return text
        // Remove Markdown headers
        .replaceAll("(?m)^#+\\s*", "") // Remove ###, ##, #
        // Remove horizontal rules
        .replaceAll("(?m)^---+$", "") // Remove lines with only dashes
        // Remove Markdown lists
        .replaceAll("(?m)^[-*]\\s+", "") // Remove leading - or *
        // Remove tables (basic cleanup for Markdown tables)
        .replaceAll("(?m)^\\|.*\\|$", "") // Remove table rows starting and ending with |
        .replaceAll("(?m)^\\|-+\\|$", "") // Remove table separators like |-----|
        // .replaceAll("(?m)^\\*\\s*(.+)", "$1") // Replace `* item` with `item`
        // .replaceAll("\\s{2,}", " ") // Replace multiple spaces with a single space
        // Trim whitespace
        .trim();
}


    @PostMapping("/saveGeneratedCourse")
    public ResponseEntity<String> saveGeneratedCourse(@RequestBody Map<String, Object> generatedCourseData) {
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            // Convert "module" to CourseModule
            CourseModule module = objectMapper.convertValue(generatedCourseData.get("module"), CourseModule.class);

            // Convert "units" to List<Unit>
            List<Unit> units = ((List<?>) generatedCourseData.get("units"))
                    .stream()
                    .map(unitData -> objectMapper.convertValue(unitData, Unit.class))
                    .collect(Collectors.toList());

            // Save the module and units
            moduleService.saveModule(module);
            units.forEach(unit -> {
                unit.setModule(module); // Associate units with the module
                unitService.saveUnit(unit);

                // Save activities (null-safe)
                if (unit.getActivityUnits() != null) {
                    unit.getActivityUnits().forEach(activityService::saveActivity);
                }

                // Save assessments, check if duration is null or empty before parsing
                Assessment assessment = new Assessment();
                assessment.setAssessmentName("Assessment for " + module.getModuleName());

                // Check if the duration is valid, if not, set it to a default value (e.g., 0 or
                // another default)
                String durationStr = module.getDuration();
                if (durationStr != null && !durationStr.isEmpty()) {
                    assessment.setDuration(Integer.parseInt(durationStr));
                } else {
                    assessment.setDuration(0); // or a default value if needed
                }

                assessment.setUnit(unit);
                assessmentService.saveAssessment(assessment);
            });

            return ResponseEntity.ok("Module, Units, Activities, and Assessments saved successfully.");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error while saving generated data: " + e.getMessage());
        }
    }

    @GetMapping("/getAllModules")
    public List<CourseModule> getAllCourseModules() {
        return moduleService.getAllCourseModules();
    }

    @GetMapping("/getAllUnits")
    public List<Unit> getAllUnits() {
        return unitService.getAllUnits();
    }

    @GetMapping("/getUnitsByModules")
public ResponseEntity<List<Unit>> getUnitsByModules(@RequestParam String moduleId) {
    System.out.println("Received moduleId: " + moduleId); // Log moduleId
    List<Unit> units = unitService.findUnitsByModuleId(moduleId);
    return ResponseEntity.ok(units);
}

}
