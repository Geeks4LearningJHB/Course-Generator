package com.geeks4learning.CourseGen.Repositories;

import java.util.List;

import org.springframework.data.jpa.repository.*;

import com.geeks4learning.CourseGen.Entities.*;

public interface activityRepository extends JpaRepository<Activity, Long>{
    List<Activity> findByUnit_Module_ModuleId(Long moduleId);
}
