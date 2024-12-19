package com.geeks4learning.CourseGen.Controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.geeks4learning.CourseGen.DTOs.PromtDTO;
import com.geeks4learning.CourseGen.Entities.Activity;
import com.geeks4learning.CourseGen.Entities.Assessment;
import com.geeks4learning.CourseGen.Entities.CourseModule;
import com.geeks4learning.CourseGen.Entities.Outline;
import com.geeks4learning.CourseGen.Entities.Unit;
import com.geeks4learning.CourseGen.Model.ChatCompletionRequest;
import com.geeks4learning.CourseGen.Model.ChatCompletionResponse;
import com.geeks4learning.CourseGen.Model.CourseRequest;
import com.geeks4learning.CourseGen.Repositories.ModuleRepository;
import com.geeks4learning.CourseGen.Repositories.OutlineRepository;
import com.geeks4learning.CourseGen.Repositories.unitRepository;
import com.geeks4learning.CourseGen.Services.ActivityService;
import com.geeks4learning.CourseGen.Services.AssessmentService;
import com.geeks4learning.CourseGen.Services.ModuleService;
import com.geeks4learning.CourseGen.Services.OutlineService;
import com.geeks4learning.CourseGen.Services.PromptService;
import com.geeks4learning.CourseGen.Services.UnitService;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Async;
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
    private ModuleRepository moduleRepository;

    @Autowired
    private OutlineService outlineService;

    @Autowired
    private unitRepository unitRepository;

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

    private Map<String, Map<String, Object>> courseCache = new ConcurrentHashMap<>();

    @PostMapping("/generateCourse")
    public ResponseEntity<Map<String, Object>> generateCourse(@RequestBody CourseRequest courseRequest) {
        Map<String, Object> response = new HashMap<>();
        try {
            // Step 1: Save the prompt
            PromtDTO newPrompt = new PromtDTO(courseRequest);
            promptService.savePrompt(newPrompt);

            // Step 2: Generate the course outline
            String moduleOutlinePrompt = "Please generate a course outline for a book teaching about: "
                    + courseRequest.getCourseTitle()
                    + " that would take "
                    + courseRequest.getDuration()
                    + " months with a difficulty level of "
                    + courseRequest.getDifficulty();
            String moduleOutline = respondToPrompt(moduleOutlinePrompt);

            // Parse the outline into lines
            String[] outlineLines = moduleOutline.split("\n");
            String outlineName = sanitizeText(outlineLines[0]); // First line is the outline name

            // Parse actual units from the remaining lines
            List<String> unitLines = Arrays.stream(outlineLines)
                    .skip(1) // Skip the first line as it is the outline name
                    .map(String::trim)
                    .filter(line -> !line.isEmpty())
                    .collect(Collectors.toList());

            // Create the Outline object
            Outline outline = new Outline();
            outline.setOutlineName(outlineName);

            // Create the CourseModule object
            CourseModule module = new CourseModule();
            module.setModuleName("Module: " + courseRequest.getCourseTitle());
            module.setUnits(new ArrayList<>());

            // Step 3: Generate content for each unit
            List<CompletableFuture<Unit>> unitTasks = unitLines.stream()
                    .map(unitName -> CompletableFuture
                            .supplyAsync(() -> createUnitContent(module, unitName, courseRequest.getCourseTitle())))
                    .collect(Collectors.toList());

            // Collect results
            List<Unit> units = unitTasks.stream()
                    .map(CompletableFuture::join)
                    .collect(Collectors.toList());
            module.setUnits(units);

            // Attach module and units to the outline
            outline.setModule(module);
            outline.setUnits(module.getUnits());

            // Store the generated course data in memory for the user to decide later
            String courseId = UUID.randomUUID().toString();
            courseCache.put(courseId, Map.of("outline", outline, "module", module, "units", units));

            // Step 4: Return the generated course data
            response.put("courseId", courseId); // Include course ID to identify the generated course
            response.put("outline", outline); // Include outline in response
            response.put("module", module);
            response.put("units", units);
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error generating course content: " + e.getMessage()));
        }
    }

    private Unit createUnitContent(CourseModule module, String unitName, String courseTitle) {
        try {
            Unit unit = new Unit();
            unit.setUnitName(sanitizeText(unitName));
            unit.setModule(module);

            // Generate unit content
            String contentPrompt = "Provide detailed content for the unit: '" + unitName + "' in the course '"
                    + courseTitle + "'.";
            unit.setContent(sanitizeText(respondToPrompt(contentPrompt)));

            // Generate activities for the unit
            String activityPrompt = "Generate activities for the unit: '" + unitName + "' in the course '" + courseTitle
                    + "'.";
            String activityContent = sanitizeText(respondToPrompt(activityPrompt));
            Activity activity = new Activity(activityContent, unit);
            unit.setActivityUnits(Collections.singletonList(activity));

            return unit;
        } catch (Exception e) {
            throw new RuntimeException("Error creating content for unit: " + unitName, e);
        }
    }

    @Async
    public CompletableFuture<Void> generateUnitContentAsync(CourseModule module, String unitName, String prompt) {
        // Log before running async task
        System.out.println("Generating content for unit: " + unitName);
        return CompletableFuture.runAsync(() -> generateUnitContent(module, unitName, prompt))
                .thenRun(() -> System.out.println("Completed content for unit: " + unitName));
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

    // private CourseModule parseModuleOutline(String moduleOutline) {
    // CourseModule courseModule = new CourseModule();
    // String[] lines = moduleOutline.split("\n");

    // // Separate metadata and units
    // for (String line : lines) {
    // String sanitizedLine = sanitizeText(line);

    // if (sanitizedLine.startsWith("Course Duration:")) {
    // courseModule.setDuration(sanitizedLine.replace("Course Duration:",
    // "").trim());
    // } else if (sanitizedLine.startsWith("Difficulty Level:")) {
    // courseModule.setModuleDescription(sanitizedLine.replace("Difficulty Level:",
    // "").trim());
    // } else if (sanitizedLine.startsWith("Target Audience:")) {
    // courseModule.setModuleDescription(
    // (courseModule.getModuleDescription() != null ?
    // courseModule.getModuleDescription() + "; " : "")
    // + sanitizedLine.replace("Target Audience:", "").trim()
    // );
    // } else if (!sanitizedLine.isEmpty() && !sanitizedLine.equals("---")) {
    // Unit unit = new Unit();
    // unit.setUnitName(sanitizedLine);
    // unit.setModule(courseModule);
    // courseModule.getUnits().add(unit);
    // }
    // }

    // return courseModule;
    // }
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
    public ResponseEntity<String> saveGeneratedCourse(@RequestParam String courseId) {
        Map<String, Object> generatedCourseData = courseCache.get(courseId);
        if (generatedCourseData == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Course not found in memory.");
        }

        try {
            ObjectMapper objectMapper = new ObjectMapper();
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

            // Optionally, remove the course from the cache after saving it
            courseCache.remove(courseId);

            return ResponseEntity.ok("Module, Units, Activities, and Assessments saved successfully.");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error while saving generated data: " + e.getMessage());
        }
    }

    @PostMapping("/discardGeneratedCourse")
    public ResponseEntity<String> discardGeneratedCourse(@RequestParam String courseId) {
        // Simply remove the course from memory if the user decides to discard it
        if (courseCache.remove(courseId) != null) {
            return ResponseEntity.ok("Course discarded successfully.");
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Course not found in memory.");
        }
    }

    @PostMapping("/regenerateText")
    public ResponseEntity<Map<String, String>> regenerateText(
            @RequestParam String unitId,
            @RequestParam String moduleId,
            @RequestBody String highlightedText) {
        try {
            // Fetch the existing module using the repository
            Optional<CourseModule> optionalModule = moduleRepository.findById(moduleId);
            if (optionalModule.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Module not found."));
            }
            CourseModule module = optionalModule.get();

            // Fetch the unit (update unitService if needed)
            Optional<Unit> optionalUnit = unitRepository.findById(unitId); // Ensure unitService supports findById
            if (optionalUnit.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Unit not found."));
            }
            Unit unit = optionalUnit.get();

            // Generate new content based on the highlighted text
            String prompt = "Rewrite or expand the following content: " + highlightedText;
            String regeneratedText = respondToPrompt(prompt);

            // Return the regenerated text to the frontend
            return ResponseEntity.ok(Map.of("regeneratedText", regeneratedText));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error regenerating text: " + e.getMessage()));
        }
    }

    @PostMapping("/confirmUpdate")
    public ResponseEntity<String> confirmUpdate(
            @RequestParam String unitId,
            @RequestBody String regeneratedText) {
        try {
            // Fetch the existing unit
            Optional<Unit> optionalUnit = unitRepository.findById(unitId);
            if (optionalUnit.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body("Unit not found with ID: " + unitId);
            }

            Unit unit = optionalUnit.get();

            // Update the unit content
            unit.setContent(regeneratedText);
            unitService.saveUnit(unit);

            return ResponseEntity.ok("Unit updated successfully.");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error updating unit: " + e.getMessage());
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

    @GetMapping("/getOutlineById")
    public Optional<Outline> getOutlineById(@RequestParam String outlineId) {
        return outlineService.findOutlineById(outlineId);
    }

}