package com.geeks4learning.CourseGen.Repositories;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.geeks4learning.CourseGen.Entities.CourseModule;

public interface ModuleRepository extends JpaRepository<CourseModule, Long> {
    List<CourseModule> findByModuleName(String moduleName);
}
