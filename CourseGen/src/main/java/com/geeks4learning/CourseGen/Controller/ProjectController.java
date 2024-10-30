package com.geeks4learning.CourseGen.Controller;

import com.geeks4learning.CourseGen.Services.AdminService;

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
import com.geeks4learning.CourseGen.Model.Message;

@RestController
@RequestMapping("/Admin")
@CrossOrigin(origins = "http://localhost:4200")
public class ProjectController {

    @Autowired
    private AdminService adminService;

    // @PostMapping("/createAdmin")
    // public Message createTrainer(@RequestBody AdminDTO adminDTO) {
    //     return adminService.createAdmin(adminDTO);
    // }

    @PostMapping("/createTrainer")
    public Message createTrainer(@RequestBody TrainerDTO TrainerDTO) {
        return adminService.createTrainer(TrainerDTO);
    }
    @PostMapping("/Adminlogin")
    public ResponseEntity<String> login(@RequestBody AdminLogin adminLogin) {
        // Call the service method to authenticate
        Message authResponse = adminService.authenticateAdmin(adminLogin.getEmail(), adminLogin.getPassword());
    
        // Check the status of the response and set appropriate HTTP status
        if ("Success".equals(authResponse.getResponse())) {
            return ResponseEntity.ok(authResponse.getMessage()); // HTTP 200 OK
        } else {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(authResponse.getMessage()); // HTTP 401 Unauthorized
        }
    }
}
