package com.geeks4learning.CourseGen.Repositories;

import org.springframework.data.jpa.repository.JpaRepository;

import com.geeks4learning.CourseGen.Entities.AdminEntity;

public interface AdminRepository extends JpaRepository<AdminEntity, Long> {

}
