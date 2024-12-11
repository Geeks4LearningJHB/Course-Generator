package com.geeks4learning.CourseGen.Services;

import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.geeks4learning.CourseGen.Entities.*;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Repositories.AdminRepository;


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
    
}
