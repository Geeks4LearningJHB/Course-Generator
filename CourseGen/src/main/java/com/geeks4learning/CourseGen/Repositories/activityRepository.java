package com.geeks4learning.CourseGen.Repositories;

import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;
import com.geeks4learning.CourseGen.Entities.Activity;

public interface activityRepository extends MongoRepository<Activity, String> {

    List<Activity> findByUnit_Module_ModuleId(String moduleId);
}
