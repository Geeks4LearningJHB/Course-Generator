package com.geeks4learning.CourseGen.Controller;

import com.geeks4learning.CourseGen.Services.AdminService;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.geeks4learning.CourseGen.DTOs.AdminDTO;
import com.geeks4learning.CourseGen.DTOs.TrainerDTO;
import com.geeks4learning.CourseGen.Entities.AdminEntity;
import com.geeks4learning.CourseGen.Model.Message;

@RestController
@RequestMapping("/Admin")
public class ProjectController {

    @Autowired
    private AdminService adminService;

    @PostMapping("/createAdmin")
    public Message createTrainer(@RequestBody AdminDTO adminDTO) {
        return adminService.createAdmin(adminDTO);
    }
}
