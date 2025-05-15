package com.geeks4learning.CourseGen.Repositories;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import com.geeks4learning.CourseGen.DTOs.TrainerDTO;
import com.geeks4learning.CourseGen.DTOs.TrainerViewDTO;
import com.geeks4learning.CourseGen.Entities.TrainerEntity;

public interface TrainerRepository extends JpaRepository<TrainerEntity, Long> {

    Optional<TrainerEntity> findByEmailAndPassword(String email, String Passsword);

    List<TrainerEntity> findByStatus(String status);

    Optional<TrainerEntity> findByEmail(String email);

    @Query("SELECT new com.geeks4learning.CourseGen.DTOs.TrainerViewDTO(t.name, t.surname, t.email, t.status) FROM TrainerEntity t")
    List<TrainerViewDTO> findAllTrainer();

    @Query("SELECT t FROM TrainerEntity t")
    List<TrainerEntity> findAllTrainers();

}
