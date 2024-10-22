package com.geeks4learning.CourseGen.Services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.geeks4learning.CourseGen.DTOs.AdminDTO;
import com.geeks4learning.CourseGen.DTOs.TrainerDTO;
import com.geeks4learning.CourseGen.Entities.AdminEntity;
import com.geeks4learning.CourseGen.Entities.TrainerEntity;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Repositories.AdminRepository;

@Service
public class AdminService {

    @Autowired
    private AdminRepository adminRepository;

    public Message createAdmin(AdminDTO adminDTO) {
        Message message = new Message();
        try {
            AdminEntity admin = new AdminEntity();
            admin.setName(adminDTO.getName());
            admin.setSurname(adminDTO.getSurname());
            admin.setEmail(adminDTO.getEmail());
            admin.setPassword(adminDTO.getPassword());

            adminRepository.save(admin);

            message.setMessage("Trainer created successfully");
            message.setResponse("Success");
        } catch (Exception e) {
            message.setMessage("Error creating trainer");
            message.setResponse("Failed");
        }
        return message;
    }

}
