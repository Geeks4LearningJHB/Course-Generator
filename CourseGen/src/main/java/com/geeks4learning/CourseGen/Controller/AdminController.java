package com.geeks4learning.CourseGen.Controller;

import java.util.*;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.geeks4learning.CourseGen.DTOs.*;
import com.geeks4learning.CourseGen.Entities.*;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Repositories.*;
import com.geeks4learning.CourseGen.Services.*;


@RestController
@RequestMapping("/Admin")
@CrossOrigin(origins = "http://localhost:4200")
public class AdminController {

    @Autowired
    private AdminRepository adminRepository;

    @Autowired
    private TrainerService trainerService;

    @Autowired
    private TrainerRepository trainerRepository;

    @Autowired
    private AdminService adminService;

    @Autowired
    private UserRepository userRepository;

    @GetMapping("/AllTrainers")
    public List<TrainerViewDTO> getTrainerDetails() {
        return trainerService.getTrainerDetails();
    }

    @PostMapping("/createAdmin")
    public Message createAdmin(@RequestBody AdminDTO adminDTO) {
        return adminService.createAdmin(adminDTO);
    }

    @PostMapping("/createTrainer")
    public Message createTrainer(@RequestBody TrainerDTO TrainerDTO) {
        return trainerService.createTrainer(TrainerDTO);
    }

    @PostMapping("/Adminlogin")
    public ResponseEntity<Message> authenticateAdmin(@RequestBody AdminDTO adminLogin) {
        Optional<AdminEntity> admin = adminRepository.findByEmailAndPassword(adminLogin.getEmail(),
                adminLogin.getPassword());

        Message message = new Message();

        if (admin.isPresent()) {
            message.setResponse("Success");
            message.setMessage("Authentication successful!");
            return ResponseEntity.ok(message);

        } else {
            message.setResponse("Failure");
            message.setMessage("Invalid email or password.");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(message);

        }
    }

    @PostMapping("/Trainerlogin")
    public ResponseEntity<String> login(@RequestBody TrainerDTO trainerLogin) {

        Message authResponse = trainerService.authenticateTrainer(trainerLogin.getEmail(), trainerLogin.getPassword());

        if ("Success".equals(authResponse.getResponse())) {
            return ResponseEntity.ok(authResponse.getMessage());
        } else {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(authResponse.getMessage());
        }
    }

    @GetMapping("/pending-trainers")
    public List<PendingDTO> getPendingTrainers() {
        List<TrainerEntity> trainers = trainerRepository.findByStatus("pending");
        return trainers.stream()
                .map(trainer -> new PendingDTO(trainer.getUserId(), trainer.getName(), trainer.getSurname(),
                        trainer.getEmail()))
                .collect(Collectors.toList());
    }

    @PostMapping("/approve-trainer/{UserId}")
    public ResponseEntity<Map<String, String>> approveTrainer(@PathVariable Long UserId) {
        Optional<TrainerEntity> trainer = trainerRepository.findById(UserId);
        if (trainer.isPresent()) {
            TrainerEntity t = trainer.get();
            t.setStatus("active");
            trainerRepository.save(t);
            // Return JSON response
            Map<String, String> response = new HashMap<>();
            response.put("message", "Trainer approved");
            return ResponseEntity.ok(response);
        }
        Map<String, String> errorResponse = new HashMap<>();
        errorResponse.put("message", "Trainer not found");
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(errorResponse);
    }

    @PostMapping("/reject-trainer/{id}")
    public ResponseEntity<Map<String, String>> rejectTrainer(@PathVariable Long id) {
        if (trainerRepository.existsById(id)) {
            trainerRepository.deleteById(id);
            // Return JSON response
            Map<String, String> response = new HashMap<>();
            response.put("message", "Trainer rejected");
            return ResponseEntity.ok(response);
        }
        Map<String, String> errorResponse = new HashMap<>();
        errorResponse.put("message", "Trainer not found");
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(errorResponse);
    }

    @PutMapping("/update-status")
    public ResponseEntity<Map<String, String>> updateTrainerStatus(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String status = request.get("status");

        Optional<TrainerEntity> trainerOptional = trainerRepository.findByEmail(email);
        if (trainerOptional.isPresent()) {
            TrainerEntity trainer = trainerOptional.get();
            trainer.setStatus(status);
            trainerRepository.save(trainer);

            Map<String, String> response = new HashMap<>();
            response.put("message", "Trainer status updated successfully.");
            return ResponseEntity.ok(response);
        } else {
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("message", "Trainer not found.");
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(errorResponse);
        }
    }

    @GetMapping("/roles")
    public ResponseEntity<Set<Role>> getRoles(@RequestParam Long userId, @RequestParam String userType) {
        // Fetch the roles based on the userId and userType
        Set<Role> roles = adminService.getRolesByUserId(userId, userType);

        // If no roles are found, return a NOT_FOUND status
        if (roles.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Collections.emptySet());
        }

        // If roles are found, return them with OK status
        return ResponseEntity.ok(roles);
    }

   

    @GetMapping("/allUsers")
    public List<BaseUser> getAllUsers() {
        List<BaseUser> allUsers = new ArrayList<>();
        // Fetch Admins and Trainers separately and combine them
        allUsers.addAll(adminRepository.findAllAdmins());
        allUsers.addAll(trainerRepository.findAllTrainers());
        return allUsers;
    }

}
