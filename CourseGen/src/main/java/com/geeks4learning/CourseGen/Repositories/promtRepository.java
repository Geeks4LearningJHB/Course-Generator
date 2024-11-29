package com.geeks4learning.CourseGen.Repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.mongodb.repository.MongoRepository;

import com.geeks4learning.CourseGen.Entities.Promt;

public interface promtRepository extends MongoRepository<Promt,String>{

}
