package com.geeks4learning.CourseGen.Controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.geeks4learning.CourseGen.DTOs.HighlightRequestDTO;
import com.geeks4learning.CourseGen.DTOs.UpdateRequestDTO;
import com.geeks4learning.CourseGen.DTOs.PromtDTO;
import com.geeks4learning.CourseGen.DTOs.RegenerationRequestsDTO;
import com.geeks4learning.CourseGen.Entities.Activity;
import com.geeks4learning.CourseGen.Entities.Assessment;
import com.geeks4learning.CourseGen.Entities.CourseModule;
import com.geeks4learning.CourseGen.Entities.Outline;
import com.geeks4learning.CourseGen.Entities.Unit;
import com.geeks4learning.CourseGen.Model.ChatCompletionRequest;
import com.geeks4learning.CourseGen.Model.ChatCompletionResponse;
import com.geeks4learning.CourseGen.Model.CourseRequest;
import com.geeks4learning.CourseGen.Repositories.ModuleRepository;
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
    private OutlineService outlineService;

    @Autowired
    private ModuleService moduleService;

    @Autowired
    private UnitService unitService;

    @Autowired
    private AssessmentService assessmentService;

    @Autowired
    private ActivityService activityService;

    @Autowired
    private ModuleRepository moduleRepository;

    @Autowired
    private unitRepository unitRepository;

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

            // Step 2: Generate structured outline
            String moduleOutlinePrompt = getStructuredOutlinePrompt(courseRequest);
            System.out.println("moduleOutlinePrompt= " + moduleOutlinePrompt);
            String moduleOutline = respondToPrompt(moduleOutlinePrompt);
            System.out.println("moduleOutline= " + moduleOutline);

            // Parse the outline
            String[] outlineLines = moduleOutline.split("\n");
            String outlineName = findOutlineName(outlineLines);
            List<Map<String, String>> unitDetails = parseUnitLines(outlineLines);

            // Create Outline and Module objects
            Outline outline = new Outline();
            outline.setOutlineName(outlineName);

            CourseModule module = new CourseModule();
            module.setModuleName("Module: " + courseRequest.getCourseTitle());
            // module.setModuleDescription("Description: " +
            // courseRequest.getDescription());
            module.setDuration(String.valueOf(courseRequest.getDuration()));
            module.setUnits(new ArrayList<>());

            // Step 3: Generate detailed content for each unit
            List<CompletableFuture<Unit>> unitTasks = unitDetails.stream()
                    .map(detail -> CompletableFuture.supplyAsync(() -> createDetailedUnitContent(
                            module,
                            detail.get("unitName"),
                            detail.get("unitDescription"),
                            courseRequest)))
                    .collect(Collectors.toList());
            // Wait for all unit tasks to complete
            List<Unit> units = unitTasks.stream()
                    .map(CompletableFuture::join)
                    .collect(Collectors.toList());

            module.setUnits(units);
            outline.setModule(module);
            outline.setUnits(units);

            // Store in cache for later saving
            String courseId = UUID.randomUUID().toString();
            courseCache.put(courseId, Map.of(
                    "outline", outline,
                    "module", module,
                    "units", units));

            // Return response
            response.put("courseId", courseId);
            response.put("outline", outline);
            response.put("module", module);
            response.put("units", units);
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error generating course: " + e.getMessage()));
        }
    }

    private Unit createDetailedUnitContent(CourseModule module, String unitName, String unitDescription,
                                       CourseRequest courseRequest) {
    Unit unit = new Unit();
    unit.setUnitId(UUID.randomUUID().toString()); // Assign a unique ID
    unit.setUnitName(sanitizeText(unitName));
    unit.setModule(module);
    unit.setUnitDescription(sanitizeText(unitDescription));

    // Generate detailed content
    String contentPrompt = String.format(
        "Create **detailed educational content** for the unit '%s' in the course '%s'. " +
        "This unit is part of a %s-level course and should provide content suitable for learners to master the topic within 1 month. " +
        "The content should be structured in a textbook format and organized into the following **detailed sections**:\n\n" +
        "1. **Introduction**:\n" +
        "- Provide a thorough overview of the topic and explain why it is important in the context of the course.\n" +
        "2. **Detailed Explanation of Theories**:\n" +
        "- Include in-depth explanations of core concepts, supported by examples and diagrams where relevant.\n" +
        "3. **Practical Examples**:\n" +
        "- Include at least 3 real-world examples or case studies related to the unit topic.\n" +
        "4. **Key Definitions and Terminology**:\n" +
        "- Include a glossary of at least 10 key terms with definitions.\n" +
        "5. **Real-World Applications**:\n" +
        "- Discuss how the topic is applied in real-life scenarios, including any historical or current applications.\n" +
        "6. **Summary and Takeaways**:\n" +
        "- Summarize the key learning points and explain their importance for future units.\n" +
        "7. **Additional Readings and Resources**:\n" +
        "- Provide at least 3 suggestions for further reading, including books, articles, or online materials.\n\n" +
        "Please ensure the content is detailed, engaging, and suitable for self-paced learning over a 1-month period.",
        unitName,
        courseRequest.getCourseTitle(),
        courseRequest.getDifficulty()
);


    String content = respondToPrompt(contentPrompt);
    unit.setContent(sanitizeText(content));

    // Generate activities
    String activityPrompt = String.format(
        "Create 3 **engaging and detailed practical activities** for the unit '%s' that align with the following goals:\n" +
        "1. Reinforce key concepts from the unit content.\n" +
        "2. Promote critical thinking and interaction.\n" +
        "3. Relate to real-world scenarios discussed in the content.\n" +
        "4. Encourage active problem-solving and collaboration.\n\n" +
        "Each activity should:\n" +
        "- Include a clear title and description.\n" +
        "- Provide step-by-step instructions.\n" +
        "- Specify the estimated time to complete (e.g., 1-2 hours).\n" +
        "- Outline expected learning outcomes.\n" +
        "- Include reflection questions to assess understanding after the activity.\n",
        unitName
);


    String activityContent = respondToPrompt(activityPrompt);
    Activity activity = new Activity(sanitizeText(activityContent), unit);
    unit.setActivityUnits(Collections.singletonList(activity));

    return unit;
}


    private String getStructuredOutlinePrompt(CourseRequest courseRequest) {
        
            return String.format(
                    "Create a **comprehensive and detailed course outline** for: '%s'.\n" +
                            "Course Duration: %d months\n" +
                            "Difficulty: %s\n\n" +
                            "The outline should include:\n" +
                            "1. **Monthly Topics**:\n" +
                            "- A detailed description of the key focus areas for each month.\n" +
                            "2. **Weekly Subtopics**:\n" +
                            "- Break each month into weekly modules with subtopics.\n" +
                            "3. **Learning Objectives**:\n" +
                            "- Define 3-5 key objectives for each week that are specific and measurable.\n" +
                            "4. **Activities and Assessments**:\n" +
                            "- Provide at least 1 practical activity or assessment per week to reinforce learning.\n\n" +
                            "Ensure the outline is designed for a self-paced learner and is structured like a detailed textbook, with clear progression and real-world applications.",
                    courseRequest.getCourseTitle(),
                    courseRequest.getDuration(),
                    courseRequest.getDifficulty()
            );  
    }

    private String findOutlineName(String[] lines) {
        for (String line : lines) {
            String trimmed = line.trim();
            if (trimmed.startsWith("Month") || trimmed.matches(".*: .*")) {
                return sanitizeText(trimmed);
            }
        }
        return Arrays.stream(lines)
                .map(String::trim)
                .filter(line -> !line.isEmpty())
                .findFirst()
                .map(this::sanitizeText)
                .orElse("Course Outline");
    }

    private List<Map<String, String>> parseUnitLines(String[] lines) {
        List<Map<String, String>> unitDetails = new ArrayList<>();
        StringBuilder currentDescription = new StringBuilder();
        String currentUnitName = null;

        for (String line : lines) {
            String trimmed = line.trim();

            if (trimmed.isEmpty() || trimmed.startsWith("Here's") || trimmed.startsWith("The course")) {
                continue; // Skip non-relevant lines
            }

            // Detect new unit (Month or Week)
            if (trimmed.startsWith("Month")) {
                if (currentUnitName != null && currentDescription.length() > 0) {
                    // Save previous unit details
                    unitDetails.add(Map.of(
                            "unitName", currentUnitName,
                            "unitDescription", currentDescription.toString().trim()));
                }
                currentUnitName = trimmed; // Set the unit name to the month title
                currentDescription = new StringBuilder(); // Start new description
            } else if (trimmed.startsWith("Week")) {
                if (currentUnitName == null) {
                    // Handle cases where "Week" appears without a preceding "Month"
                    currentUnitName = "General Course Outline";
                }
                currentDescription.append(trimmed).append("\n");
            } else {
                // Append additional lines to the current unit description
                currentDescription.append(trimmed).append("\n");
            }
        }

        // Add the last unit
        if (currentUnitName != null && currentDescription.length() > 0) {
            unitDetails.add(Map.of(
                    "unitName", currentUnitName,
                    "unitDescription", currentDescription.toString().trim()));
        }

        return unitDetails;
    }

    private String respondToPrompt(String prompt) {
        ChatCompletionRequest chatCompletionRequest = new ChatCompletionRequest("gpt-4o-mini", prompt);
        ChatCompletionResponse chatCompletionResponse = restTemplate.postForObject(completionsURL,
                chatCompletionRequest, ChatCompletionResponse.class);
        assert chatCompletionResponse != null;
        String rawContent = chatCompletionResponse.getChoices().get(0).getMessage().getContent();
        return sanitizeText(rawContent);
    }

    private String sanitizeText(String text) {
        return text
                .replaceAll("(?m)^#+\\s*", "") // Remove markdown headings
                .replaceAll("(?m)^---+$", "") // Remove separators
                .replaceAll("(?m)^(\\d+\\.\\s)", "$1 ") // Ensure numbering is consistent
                .replaceAll("(?m)^(\\*\\s)", "• ") // Use bullet points for lists
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
            CourseModule module = objectMapper.convertValue(generatedCourseData.get("module"), CourseModule.class);
            List<Unit> units = ((List<?>) generatedCourseData.get("units"))
                    .stream()
                    .map(unitData -> objectMapper.convertValue(unitData, Unit.class))
                    .collect(Collectors.toList());

            moduleService.saveModule(module);
            units.forEach(unit -> {
                unit.setModule(module);
                unitService.saveUnit(unit);

                if (unit.getActivityUnits() != null) {
                    unit.getActivityUnits().forEach(activityService::saveActivity);
                }

                Assessment assessment = new Assessment();
                assessment.setAssessmentName("Assessment for " + module.getModuleName());
                String durationStr = module.getDuration();
                assessment
                        .setDuration(durationStr != null && !durationStr.isEmpty() ? Integer.parseInt(durationStr) : 0);
                assessment.setUnit(unit);
                assessmentService.saveAssessment(assessment);
            });

            courseCache.remove(courseId);
            return ResponseEntity.ok("Module, Units, Activities, and Assessments saved successfully.");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error while saving generated data: " + e.getMessage());
        }
    }

    @PostMapping("/regenerateText")
    public ResponseEntity<Map<String, String>> regenerateText(
            @RequestBody HighlightRequestDTO requestDTO) {
        try {
            Optional<CourseModule> optionalModule = moduleRepository.findById(requestDTO.getModuleId());
            if (optionalModule.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Module not found."));
            }

            Optional<Unit> optionalUnit = unitRepository.findById(requestDTO.getUnitId());
            if (optionalUnit.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Unit not found."));
            }

            String prompt = "Rewrite the following content: " + requestDTO.getHighlightedText();
            String regeneratedText = respondToPrompt(prompt);   
            
            return ResponseEntity.ok(Map.of(
                    "regeneratedText", regeneratedText,
                    "startIndex", String.valueOf(requestDTO.getStartIndex()),
                    "endIndex", String.valueOf(requestDTO.getEndIndex())));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error regenerating text: " + e.getMessage()));
        }
    }

    @PostMapping("/confirmUpdate")
    public ResponseEntity<Map<String, String>> confirmUpdate(
            @RequestBody UpdateRequestDTO updateDTO) {
        try {
            Optional<Unit> optionalUnit = unitRepository.findById(updateDTO.getUnitId());
            if (optionalUnit.isEmpty()) {
                Map<String, String> response = new HashMap<>();
                response.put("error", "Unit not found with ID: " + updateDTO.getUnitId());
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
            }

            Unit unit = optionalUnit.get();
            String currentContent = unit.getContent();

            // Replace only the highlighted portion with regenerated text
            String updatedContent = currentContent.substring(0, updateDTO.getStartIndex()) +
                    updateDTO.getRegeneratedText() +
                    currentContent.substring(updateDTO.getEndIndex());

            unit.setContent(updatedContent);
            unitService.saveUnit(unit);

            Map<String, String> response = new HashMap<>();
            response.put("message", "Unit updated successfully.");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, String> response = new HashMap<>();
            response.put("error", "Error updating unit: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @PostMapping("/regenerateUnitWithReason")
    public ResponseEntity<Map<String, String>> regenerateUnitWithReason(
            @RequestBody RegenerationRequestsDTO requestDTO) {
        try {
            // Find the module by its ID (as a String)
            Optional<CourseModule> optionalModule = moduleRepository.findById(requestDTO.getModuleId());
            if (optionalModule.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Module not found."));
            }

            // Find the unit by its ID (as a String)
            Optional<Unit> optionalUnit = unitRepository.findById(requestDTO.getUnitId());
            if (optionalUnit.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Unit not found."));
            }

            // Validate the reason
            if (requestDTO.getReason() == null || requestDTO.getReason().isBlank()) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body(Map.of("error", "Reason for regeneration is required."));
            }

            // Generate the prompt
            String prompt = String.format(
                    "Rewrite the content for the unit '%s' under the module '%s' for the following reason: %s",
                    optionalUnit.get().getUnitName(),
                    optionalModule.get().getModuleName(),
                    requestDTO.getReason());

            // Call ChatGPT to regenerate text
            String regeneratedText = respondToPrompt(prompt);

            // Save or process the regenerated text as needed
            Unit unit = optionalUnit.get();
            unit.setContent(sanitizeText(regeneratedText));
            unitRepository.save(unit);

            // Return the response
            return ResponseEntity.ok(Map.of(
                    "message", "Unit content regenerated successfully.",
                    "unitId", unit.getUnitId(),
                    "regeneratedContent", regeneratedText));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error regenerating unit content: " + e.getMessage()));
        }
    }

    @GetMapping("/getAllModules")
    public List<CourseModule> getAllCourseModules() {
        return moduleService.getAllCourseModules();
    }

    @GetMapping("/getModuleById")
    public Optional<CourseModule> getModuleById(@RequestParam String id) {
        return moduleService.findCourseModuleById(id);
    }

    @GetMapping("/getAllUnits")
    public List<Unit> getAllUnits() {
        return unitService.getAllUnits();
    }

    @GetMapping("/getUnitsByModules")
    public ResponseEntity<List<Unit>> getUnitsByModules(@RequestParam String moduleId) {
        List<Unit> units = unitService.findUnitsByModuleId(moduleId);
        return ResponseEntity.ok(units);
    }

    @GetMapping("/getOutlineById")
    public Optional<Outline> getOutlineById(@RequestParam String outlineId) {
        return outlineService.findOutlineById(outlineId);
    }
}