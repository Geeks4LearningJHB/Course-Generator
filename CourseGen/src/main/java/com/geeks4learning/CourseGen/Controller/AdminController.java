package com.geeks4learning.CourseGen.Controller;

import com.geeks4learning.CourseGen.Services.AdminService;
import com.geeks4learning.CourseGen.Services.TrainerService;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.geeks4learning.CourseGen.DTOs.AdminDTO;
import com.geeks4learning.CourseGen.DTOs.PendingDTO;
import com.geeks4learning.CourseGen.DTOs.TrainerDTO;
import com.geeks4learning.CourseGen.Entities.AdminEntity;
import com.geeks4learning.CourseGen.Entities.TrainerEntity;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Repositories.AdminRepository;
import com.geeks4learning.CourseGen.Repositories.TrainerRepository;

@RestController
@RequestMapping("/Admin")
@CrossOrigin(origins = "http://localhost:4200")
public class AdminController {

    @Autowired
    private AdminService adminService;

    @Autowired
    private AdminRepository adminRepository;

    @Autowired
    private TrainerService trainerService;

    @Autowired
    private TrainerRepository trainerRepository;

    // @PostMapping("/createAdmin")
    // public Message createTrainer(@RequestBody AdminDTO adminDTO) {
    // return adminService.createAdmin(adminDTO);
    // }

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

   // Backend Controller - Example
@GetMapping("/pending-trainers")
public List<PendingDTO> getPendingTrainers() {
    List<TrainerEntity> trainers = trainerRepository.findByStatus("pending");
    return trainers.stream()
                   .map(trainer -> new PendingDTO(trainer.getUserId(), trainer.getName(), trainer.getSurname()))
                   .collect(Collectors.toList());
}

    

    @PostMapping("/approve-trainer/{UserId}")
    public ResponseEntity<?> approveTrainer(@PathVariable Long UserId) {
        Optional<TrainerEntity> trainer = trainerRepository.findById(UserId);
        if (trainer.isPresent()) {
            TrainerEntity t = trainer.get();
            t.setStatus("active");
            trainerRepository.save(t);
            return ResponseEntity.ok("Trainer approved");
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Trainer not found");
    }

    @PostMapping("/reject-trainer/{id}")
    public ResponseEntity<?> rejectTrainer(@PathVariable Long id) {
        trainerRepository.deleteById(id);
        return ResponseEntity.ok("Trainer rejected");
    }

//     @PostMapping("/reset-password")
//     public ResponseEntity<String> resetPassword(@RequestParam String email, @RequestParam String newPassword) {
//         TrainerEntity user = trainerRepository.findByEmail(email);
//         if (user != null) {
//             user.setPassword(newPassword);  // In a real-world scenario, hash the password
//             trainerRepository.save(user);
//             return ResponseEntity.ok("Password reset successfully.");
//         } else {
//             return ResponseEntity.badRequest().body("User with the provided email does not exist.");
//         }
//     }
 }
