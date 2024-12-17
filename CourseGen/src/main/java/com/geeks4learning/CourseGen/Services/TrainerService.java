package com.geeks4learning.CourseGen.Services;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.geeks4learning.CourseGen.DTOs.TrainerDTO;
import com.geeks4learning.CourseGen.DTOs.TrainerViewDTO;
import com.geeks4learning.CourseGen.Entities.TrainerEntity;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Repositories.TrainerRepository;

@Service
public class TrainerService {

    @Autowired
    private TrainerRepository trainerRepository;

    public Message authenticateTrainer(String email, String password) {
        Optional<TrainerEntity> trainer = trainerRepository.findByEmailAndPassword(email, password);

        Message message = new Message();

        if (trainer.isPresent()) {
            TrainerEntity foundTrainer = trainer.get();

            if ("active".equalsIgnoreCase(foundTrainer.getStatus())) {
                message.setResponse("Success");
                message.setMessage("Authentication successful!");
            } else {
                message.setResponse("Failure");
                message.setMessage("Your account has not been approved by the admin.");
            }
        } else {
            message.setResponse("Failure");
            message.setMessage("Invalid email or password.");
        }

        return message;
    }

    public Message createTrainer(TrainerDTO trainerDTO) {
        Message message = new Message();
        try {
            TrainerEntity Trainer = new TrainerEntity();
            Trainer.setName(trainerDTO.getName());
            Trainer.setSurname(trainerDTO.getSurname());
            Trainer.setEmail(trainerDTO.getEmail());
            Trainer.setPassword(trainerDTO.getPassword());

            trainerRepository.save(Trainer);
            System.out.println(Trainer);
            message.setMessage("Trainer created successfully");
            message.setResponse("Success");

        } catch (Exception e) {
            message.setMessage("Error creating trainer");
            message.setResponse("Failed");
            e.printStackTrace();
        }
        return message;
    }

    public List<TrainerViewDTO> getTrainerDetails() {
        return trainerRepository.findAllTrainerDetails();
    }
    // //Get all accepted trainers
    // public List<TrainerEntity> getAcceptedTrainers() {
    // return trainerRepository.findByStatus();
    // }

}
