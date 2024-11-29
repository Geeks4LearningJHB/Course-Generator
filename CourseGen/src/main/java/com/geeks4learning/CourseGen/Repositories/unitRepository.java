package com.geeks4learning.CourseGen.Repositories;

import java.util.List;

import org.springframework.data.jpa.repository.*;
import org.springframework.data.mongodb.repository.MongoRepository;

import com.geeks4learning.CourseGen.Entities.*;

public interface unitRepository extends MongoRepository<Unit, String> {
    List<Unit> findByModule_ModuleId(Long moduleId);
}
