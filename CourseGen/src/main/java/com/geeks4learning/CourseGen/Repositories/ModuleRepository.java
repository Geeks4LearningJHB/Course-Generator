package com.geeks4learning.CourseGen.Repositories;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.mongodb.repository.MongoRepository;

import com.geeks4learning.CourseGen.Entities.CourseModule;

public interface ModuleRepository extends MongoRepository<CourseModule, String> {
    List<CourseModule> findByModuleName(String moduleName);
    Optional<CourseModule> findById(String moduleId);
    

}
