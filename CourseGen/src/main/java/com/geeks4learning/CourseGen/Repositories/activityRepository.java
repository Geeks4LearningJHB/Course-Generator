package com.geeks4learning.CourseGen.Repositories;

import org.springframework.data.mongodb.repository.MongoRepository;
import com.geeks4learning.CourseGen.Entities.Activity;

public interface activityRepository extends MongoRepository<Activity, String> {
    // Custom query methods if needed
}
