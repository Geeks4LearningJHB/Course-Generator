package com.geeks4learning.CourseGen.Controller;

import com.geeks4learning.CourseGen.Services.AdminService;
import com.geeks4learning.CourseGen.Services.TrainerService;

import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.geeks4learning.CourseGen.DTOs.AdminLogin;
import com.geeks4learning.CourseGen.DTOs.TrainerDTO;
import com.geeks4learning.CourseGen.DTOs.TrainerLogin;
import com.geeks4learning.CourseGen.Entities.AdminEntity;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Repositories.AdminRepository;

@RestController
@RequestMapping("/Admin")
@CrossOrigin(origins = "http://localhost:4200")
public class ProjectController {

    @Autowired
    private AdminService adminService;

    @Autowired
    private AdminRepository adminRepository;

    @Autowired
    private TrainerService trainerService;

    // @PostMapping("/createAdmin")
    // public Message createTrainer(@RequestBody AdminDTO adminDTO) {
    // return adminService.createAdmin(adminDTO);
    // }

    @PostMapping("/createTrainer")
    public Message createTrainer(@RequestBody TrainerDTO TrainerDTO) {
        return trainerService.createTrainer(TrainerDTO);
    }

    @PostMapping("/Adminlogin")
    public ResponseEntity<Message> authenticateAdmin(@RequestBody AdminLogin adminLogin) {
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
    public ResponseEntity<String> login(@RequestBody TrainerLogin trainerLogin) {

        Message authResponse = trainerService.authenticateTrainer(trainerLogin.getEmail(), trainerLogin.getPassword());

        if ("Success".equals(authResponse.getResponse())) {
            return ResponseEntity.ok(authResponse.getMessage());
        } else {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(authResponse.getMessage());
        }
    }
}
