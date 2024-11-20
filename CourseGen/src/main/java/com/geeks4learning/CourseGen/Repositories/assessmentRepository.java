package com.geeks4learning.CourseGen.Repositories;

import java.util.List;

import org.springframework.data.jpa.repository.*;
import org.springframework.data.mongodb.repository.MongoRepository;

import com.geeks4learning.CourseGen.Entities.Assessment;

public interface assessmentRepository extends MongoRepository<Assessment,String> {
    List<Assessment> findByUnit_Module_ModuleId(String moduleId);
}
