package com.geeks4learning.CourseGen.Controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.geeks4learning.CourseGen.DTOs.AdminDTO;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Services.AdminService;
import com.geeks4learning.CourseGen.Services.TrainerService;


@RestController
@RequestMapping("/Admin")
public class ProjectController {

    @Autowired
    private AdminService adminService;
    private TrainerService trainerService;

    @PostMapping("/createAdmin")
    public Message createTrainer(@RequestBody AdminDTO adminDTO) {

        return adminService.createAdmin(adminDTO);
    }

    @PutMapping("/{id}/accept")
    public ResponseEntity<String> acceptTrainer(@PathVariable Long id) {
        trainerService.acceptTrainer(id);
        return ResponseEntity.ok("Trainer accepted successfully");
    }

    @PutMapping("/{id}/reject")
    public ResponseEntity<String> rejectTrainer(@PathVariable Long id) {
        trainerService.rejectTrainer(id);
        return ResponseEntity.ok("Trainer rejected successfully");
    }
   
    
}
