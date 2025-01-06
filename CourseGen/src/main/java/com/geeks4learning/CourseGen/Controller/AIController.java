package com.geeks4learning.CourseGen.Controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.geeks4learning.CourseGen.DTOs.HighlightRequestDTO;
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
            String moduleOutline = respondToPrompt(moduleOutlinePrompt);

            // Parse the outline
            String[] outlineLines = moduleOutline.split("\n");
            String outlineName = findOutlineName(outlineLines);
            List<String> unitLines = parseUnitLines(outlineLines);

            // Create Outline and Module objects
            Outline outline = new Outline();
            outline.setOutlineName(outlineName);

            CourseModule module = new CourseModule();
            module.setModuleName("Module: " + courseRequest.getCourseTitle());
            module.setDuration(String.valueOf(courseRequest.getDuration()));
            module.setUnits(new ArrayList<>());

            // Step 3: Generate detailed content for each unit
            List<CompletableFuture<Unit>> unitTasks = unitLines.stream()
                .map(unitName -> CompletableFuture.supplyAsync(() -> 
                    createDetailedUnitContent(module, unitName, courseRequest)))
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
                "units", units
            ));

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

    private Unit createDetailedUnitContent(CourseModule module, String unitName, CourseRequest courseRequest) {
        Unit unit = new Unit();
        String sanitizedUnitName = sanitizeText(unitName);
        unit.setUnitName(sanitizedUnitName);
        unit.setModule(module);

        // Generate detailed content
        String contentPrompt = String.format(
            "Create detailed educational content for the unit '%s' in the course '%s'. " +
            "The content should be suitable for %s difficulty level and include:\n" +
            "1. Key concepts and theories\n" +
            "2. Practical examples\n" +
            "3. Important definitions\n" +
            "4. Real-world applications",
            sanitizedUnitName,
            courseRequest.getCourseTitle(),
            courseRequest.getDifficulty()
        );
        String content = respondToPrompt(contentPrompt);
        unit.setContent(sanitizeText(content));

        // Generate activities
        String activityPrompt = String.format(
            "Create 3 engaging practical activities for '%s' that:\n" +
            "1. Reinforce key concepts\n" +
            "2. Promote active learning\n" +
            "3. Are appropriate for %s difficulty level",
            sanitizedUnitName,
            courseRequest.getDifficulty()
        );
        String activityContent = respondToPrompt(activityPrompt);
        Activity activity = new Activity(sanitizeText(activityContent), unit);
        unit.setActivityUnits(Collections.singletonList(activity));

        return unit;
    }

    private String getStructuredOutlinePrompt(CourseRequest courseRequest) {
        return String.format(
            "Create a detailed course outline for: '%s'\n" +
            "Duration: %d months\n" +
            "Difficulty: %s\n\n" +
            "Format the outline with:\n" +
            "1. Monthly topics (e.g., 'Month 1: Foundation')\n" +
            "2. Weekly subtopics under each month\n" +
            "3. Key learning objectives for each week\n" +
            "Please ensure progressive difficulty and logical flow between topics.",
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

    private List<String> parseUnitLines(String[] lines) {
        List<String> unitLines = new ArrayList<>();
        StringBuilder currentSection = new StringBuilder();
        boolean isProcessingSection = false;

        for (String line : lines) {
            String trimmed = line.trim();
            
            if (trimmed.isEmpty() || trimmed.startsWith("Here's") || trimmed.startsWith("The course")) {
                continue;
            }

            if (trimmed.startsWith("Month") || trimmed.startsWith("Week")) {
                if (isProcessingSection && currentSection.length() > 0) {
                    unitLines.add(currentSection.toString().trim());
                }
                currentSection = new StringBuilder(trimmed);
                isProcessingSection = true;
            } else if (isProcessingSection && (trimmed.startsWith("•") || trimmed.startsWith("-"))) {
                currentSection.append("\n").append(trimmed);
            }
        }

        if (currentSection.length() > 0) {
            unitLines.add(currentSection.toString().trim());
        }

        return unitLines;
    }

    private String respondToPrompt(String prompt) {
        ChatCompletionRequest request = new ChatCompletionRequest("gpt-4o-mini", prompt);
        ChatCompletionResponse response = restTemplate.postForObject(
            completionsURL,
            request,
            ChatCompletionResponse.class
        );
        assert response != null;
        return sanitizeText(response.getChoices().get(0).getMessage().getContent());
    }

    private String sanitizeText(String text) {
        return text
            .replaceAll("(?m)^#+\\s*", "")
            .replaceAll("(?m)^---+$", "")
            .replaceAll("(?m)^[-*]\\s+", "• ")
            .replaceAll("(?m)^\\|.*\\|$", "")
            .replaceAll("(?m)^\\|-+\\|$", "")
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
                assessment.setDuration(durationStr != null && !durationStr.isEmpty() ? 
                    Integer.parseInt(durationStr) : 0);
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

    @PostMapping("/discardGeneratedCourse")
    public ResponseEntity<String> discardGeneratedCourse(@RequestParam String courseId) {
        if (courseCache.remove(courseId) != null) {
            return ResponseEntity.ok("Course discarded successfully.");
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Course not found in memory.");
    }

    @PostMapping("/regenerateText")
    public ResponseEntity<Map<String, String>> regenerateText(
            @RequestBody HighlightRequestDTO requestDTO) {
        try {
            // Fetch the existing module using the repository
            Optional<CourseModule> optionalModule = moduleRepository.findById(requestDTO.getModuleId());
            if (optionalModule.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Module not found."));
            }

            // Fetch the unit using the repository
            Optional<Unit> optionalUnit = unitRepository.findById(requestDTO.getUnitId());
            if (optionalUnit.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Unit not found."));
            }

            // Generate new content based on the highlighted text
            String prompt = "Rewrite or expand the following content: " + requestDTO.getHighlightedText();
            String regeneratedText = respondToPrompt(prompt);

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
        List<Unit> units = unitService.findUnitsByModuleId(moduleId);
        return ResponseEntity.ok(units);
    }

    @GetMapping("/getOutlineById")
    public Optional<Outline> getOutlineById(@RequestParam String outlineId) {
        return outlineService.findOutlineById(outlineId);
    }
}