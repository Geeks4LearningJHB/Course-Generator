package com.geeks4learning.CourseGen.Repositories;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import com.geeks4learning.CourseGen.Entities.BaseUser;

public interface UserRepository extends JpaRepository<BaseUser, Long> {

   
}

