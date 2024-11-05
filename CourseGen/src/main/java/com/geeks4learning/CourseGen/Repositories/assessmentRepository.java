package com.geeks4learning.CourseGen.Repositories;

import java.util.List;

import org.springframework.data.jpa.repository.*;

import com.geeks4learning.CourseGen.Entities.Assessment;

public interface assessmentRepository extends JpaRepository<Assessment,Long> {
    List<Assessment> findByUnit_Module_ModuleId(Long moduleId);
}
