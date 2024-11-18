package com.geeks4learning.CourseGen.Repositories;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import com.geeks4learning.CourseGen.Entities.TrainerEntity;

public interface TrainerRepository extends JpaRepository<TrainerEntity,Long> {

    Optional<TrainerEntity> findByEmailAndPassword(String email,String Passsword);
    List<TrainerEntity> findByStatus(String status);
    TrainerEntity findByEmail(String email);
}
