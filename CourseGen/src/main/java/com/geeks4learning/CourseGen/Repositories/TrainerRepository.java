package com.geeks4learning.CourseGen.Repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import com.geeks4learning.CourseGen.Entities.TrainerEntity;

public interface TrainerRepository extends JpaRepository<TrainerEntity,Long> {

}
