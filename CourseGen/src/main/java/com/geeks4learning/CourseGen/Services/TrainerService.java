package com.geeks4learning.CourseGen.Services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.geeks4learning.CourseGen.Entities.TrainerEntity;
import com.geeks4learning.CourseGen.Repositories.TrainerRepository;

import jakarta.transaction.Transactional;

@Service
public class TrainerService {

    @Autowired
    private TrainerRepository trainerRepository;

    public TrainerEntity getTrainerById(Long id){
        return trainerRepository.findById(id)
        .orElseThrow(() -> new RuntimeException("Trainer not found"));

    }

   
    @Transactional
    public TrainerEntity acceptTrainer(Long id){
        TrainerEntity trainer = getTrainerById(id);
        trainer.setStatus(TrainerEntity.Status.ACCEPTED);
        return trainerRepository.save(trainer);
    }


}
