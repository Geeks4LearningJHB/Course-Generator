package com.geeks4learning.CourseGen.Services;

import java.util.HashSet;
import java.util.Optional;
import java.util.Set;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.geeks4learning.CourseGen.DTOs.AdminDTO;
import com.geeks4learning.CourseGen.Entities.*;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Repositories.AdminRepository;
import com.geeks4learning.CourseGen.Repositories.RoleRepository;
import com.geeks4learning.CourseGen.Repositories.TrainerRepository;
import java.util.Collections;



@Service
public class AdminService {

    @Autowired
    private AdminRepository adminRepository;

    @Autowired
    private TrainerRepository trainerRepository;

    @Autowired
    private RoleRepository roleRepository;

public Message createAdmin(AdminDTO adminDTO) {
    Message message = new Message();
    try {
        AdminEntity admin = new AdminEntity();
        admin.setName(adminDTO.getName());
        admin.setSurname(adminDTO.getSurname());
        admin.setEmail(adminDTO.getEmail());
        admin.setPassword(adminDTO.getPassword());

        // Assign roles to admin
        Role adminRole = roleRepository.findByRoleName("Administrator")
                                       .orElseThrow(() -> new RuntimeException("Role not found"));
        admin.getRoles().add(adminRole);

        adminRepository.save(admin);
        message.setMessage("Admin created successfully");
        message.setResponse("Success");

    } catch (Exception e) {
        message.setMessage("Error creating admin");
        message.setResponse("Failed");
        e.printStackTrace();
    }
    return message;
}




   

    public Message authenticateAdmin(String email, String password) {
        Optional<AdminEntity> admin = adminRepository.findByEmailAndPassword(email, password);

        Message message = new Message();
    
        if (admin.isPresent()) {
            message.setMessage("password");
            message.setResponse("password");
        } else {
            message.setResponse("Failure");
            message.setMessage("Invalid email or password.");
        }
    
        return message; 
    }
    
    public Set<Role> getRolesByUserId(Long userId, String userType) {
        if (userType.equalsIgnoreCase("Admin")) {
            // Fetch roles for Admin using userId
            return adminRepository.findById(userId)
                    .map(AdminEntity::getRoles)
                    .orElse(Collections.emptySet());
        } else if (userType.equalsIgnoreCase("Trainer")) {
            // Fetch roles for Trainer using userId
            return trainerRepository.findById(userId)
                    .map(TrainerEntity::getRoles)
                    .orElse(Collections.emptySet());
        }
        // Return an empty set if userType is not found
        return Collections.emptySet();
    }
    
    
}
