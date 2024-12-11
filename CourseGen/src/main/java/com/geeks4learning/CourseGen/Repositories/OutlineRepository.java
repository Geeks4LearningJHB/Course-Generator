package com.geeks4learning.CourseGen.Repositories;

import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.geeks4learning.CourseGen.Entities.*;

public interface OutlineRepository extends MongoRepository<Outline,String> {
    public List<Outline> findByModule_ModuleId(String moduleId);

}
