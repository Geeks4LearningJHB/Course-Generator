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

    public Message savePrompt(PromtDTO promptDTO) {
        Message message = new Message();

        Promt prompt = modelMapper.map(promptDTO, Promt.class);

        Promt savedPromt = promptRepository.save(prompt);

        if (savedPromt.getPromtId() > 0 && savedPromt != null) {
            message.setMessage("Promt saved");
            message.setResponse("Status OK");
        }else{
            message.setMessage("error while saving");
            message.setResponse("Please rectify error");
        }
        return message;
    }

    public Promt findPromptById(Long id) {
        return promptRepository.findById(id).orElse(null);
    }
}
