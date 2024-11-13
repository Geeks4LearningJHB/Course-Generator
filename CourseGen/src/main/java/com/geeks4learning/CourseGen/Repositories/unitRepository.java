package com.geeks4learning.CourseGen.Repositories;

import java.util.List;

import org.springframework.data.jpa.repository.*;

import com.geeks4learning.CourseGen.Entities.*;

public interface unitRepository extends JpaRepository<Unit, Long> {
    List<Unit> findByModule_ModuleId(Long moduleId);
}
