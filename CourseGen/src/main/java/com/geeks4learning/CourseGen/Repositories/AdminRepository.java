package com.geeks4learning.CourseGen.Repositories;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import com.geeks4learning.CourseGen.Entities.AdminEntity;

public interface AdminRepository extends JpaRepository<AdminEntity, Long> {
    Optional<AdminEntity> findByEmailAndPassword(String Email, String Password);
    
    @Query("SELECT a FROM AdminEntity a")
    List<AdminEntity> findAllAdmins();
}


