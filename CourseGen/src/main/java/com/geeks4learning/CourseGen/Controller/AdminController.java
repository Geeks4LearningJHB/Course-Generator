package com.geeks4learning.CourseGen.Controller;
 
import java.util.*;
import java.util.Optional;
import java.util.*;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.geeks4learning.CourseGen.DTOs.AdminDTO;
import com.geeks4learning.CourseGen.DTOs.PendingDTO;
import com.geeks4learning.CourseGen.DTOs.TrainerDTO;
import com.geeks4learning.CourseGen.DTOs.TrainerViewDTO;
import com.geeks4learning.CourseGen.Entities.AdminEntity;
import com.geeks4learning.CourseGen.Entities.TrainerEntity;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Repositories.AdminRepository;
import com.geeks4learning.CourseGen.Repositories.TrainerRepository;
import com.geeks4learning.CourseGen.Services.TrainerService;
 
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
 
    // @PostMapping("/createAdmin")
    // public Message createTrainer(@RequestBody AdminDTO adminDTO) {
    // return adminService.createAdmin(adminDTO);
    // }

    @GetMapping("/AllTrainers")
   public List<TrainerViewDTO> getTrainerDetails() {
    return trainerService.getTrainerDetails();
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
                   .map(trainer -> new PendingDTO(trainer.getUserId(), trainer.getName(), trainer.getSurname(), trainer.getEmail()))
                   .collect(Collectors.toList());
}

    // @GetMapping("/pending-trainers")
    // public List<PendingDTO> getPendingTrainers() {
    //     List<TrainerEntity> trainers = trainerRepository.findByStatus("pending");
    //     return trainers.stream()
    //             .map(trainer -> new PendingDTO(trainer.getUserId(), trainer.getName(), trainer.getSurname(), trainer.getEmail()))
    //             .collect(Collectors.toList());
    // }

    // @GetMapping("/pending-trainers")
    // public List<PendingDTO> getPendingTrainers() {
    //     List<TrainerEntity> trainers = trainerRepository.findByStatus("pending");
    //     return trainers.stream()
    //             .map(trainer -> new PendingDTO(trainer.getUserId(), trainer.getName(), trainer.getSurname(), trainer.getEmail()))
    //             .collect(Collectors.toList());
    // }

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


        // Return JSON response
        Map<String, String> response = new HashMap<>();
        response.put("message", "Trainer rejected");
        return ResponseEntity.ok(response);
    }
    Map<String, String> errorResponse = new HashMap<>();
    errorResponse.put("message", "Trainer not found");
    return ResponseEntity.status(HttpStatus.NOT_FOUND).body(errorResponse);
}

}
