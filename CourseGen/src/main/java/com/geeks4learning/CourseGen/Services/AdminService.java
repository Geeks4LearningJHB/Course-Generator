package com.geeks4learning.CourseGen.Services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.geeks4learning.CourseGen.DTOs.AdminDTO;
import com.geeks4learning.CourseGen.DTOs.TrainerDTO;
import com.geeks4learning.CourseGen.Entities.*;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Repositories.AdminRepository;
import com.geeks4learning.CourseGen.Repositories.TrainerRepository;

@Service
public class AdminService {

    @Autowired
    private AdminRepository adminRepository;


    // public Message createAdmin(AdminDTO adminDTO) {
    // Message message = new Message();
    // try {
    // AdminEntity admin = new AdminEntity();
    // admin.setName(adminDTO.getName());
    // admin.setSurname(adminDTO.getSurname());
    // admin.setEmail(adminDTO.getEmail());
    // admin.setPassword(adminDTO.getPassword());

    // adminRepository.save(admin);
    // System.out.println(admin);
    // message.setMessage("Admin created successfully");
    // message.setResponse("Success");

    // } catch (Exception e) {
    // message.setMessage("Error creating Admin");
    // message.setResponse("Failed");
    // e.printStackTrace();
    // }
    // return message;
    // }

   

    public Message authenticateAdmin(String email, String password) {
        // Check if user exists with matching credentials
        AdminEntity admin = adminRepository.findByEmailAndPassword(email, password);
    
        // Create a response Message object
        Message message = new Message();
    
        if (admin != null) {
            // Admin found with matching credentials
            message.setResponse("Success");
            message.setMessage("Authentication successful!");
        } else {
            // No matching admin found
            message.setResponse("Failure");
            message.setMessage("Invalid email or password.");
        }
    
        return message;
    }
}
