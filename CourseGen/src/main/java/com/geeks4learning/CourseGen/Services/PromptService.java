package com.geeks4learning.CourseGen.Services;

import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.geeks4learning.CourseGen.DTOs.PromtDTO;
import com.geeks4learning.CourseGen.Entities.Promt;
import com.geeks4learning.CourseGen.Model.Message;
import com.geeks4learning.CourseGen.Repositories.promtRepository;

@Service
public class PromptService {

    @Autowired
    private promtRepository promptRepository;

    @Autowired
    private ModelMapper modelMapper;

    public Promt savePrompt(PromtDTO promptDTO) {
        Promt prompt = modelMapper.map(promptDTO, Promt.class);
    
        try {
            // Save the prompt
            Promt savedPromt = promptRepository.save(prompt);
    
            // Check if the save was successful
            if (savedPromt.getPromtId() != null) {
                return savedPromt; // Return the saved Promt
            } else {
                throw new RuntimeException("Failed to save the prompt");
            }
        } catch (Exception e) {
            throw new RuntimeException("An exception occurred: " + e.getMessage());
        }
    }
    
    

    // public Promt findPromptById(Long id) {
    //     return promptRepository.findById(id).orElse(null);
    // }
    }
