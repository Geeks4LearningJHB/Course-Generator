package com.geeks4learning.CourseGen.Repositories;

import org.springframework.data.jpa.repository.JpaRepository;

import com.geeks4learning.CourseGen.Entities.TrainerEntity;

public interface TrainerRepository extends JpaRepository<TrainerEntity,Long> {

    //Optional<TrainerEntity> findTrainerById(Long id);
    // Long findTrainerById (Long UserId);

    // public TrainerEntity getTrainerById(Long id);
    // TrainerEntity acceptTrainer(Long id);

}
