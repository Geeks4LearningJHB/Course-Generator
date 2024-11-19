package com.geeks4learning.CourseGen.Services;

import java.util.List;
import java.util.stream.Collectors;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.geeks4learning.CourseGen.DTOs.UnitDTO;
import com.geeks4learning.CourseGen.Entities.Unit;
import com.geeks4learning.CourseGen.Repositories.unitRepository;

@Service
public class UnitService {

    @Autowired
    private unitRepository unitRepository;

    public Unit saveUnit(Unit unit) {
        return unitRepository.save(unit);
    }

    @Transactional
    public List<Unit> findUnitsByModuleId(Long moduleId) {
        return unitRepository.findByModule_ModuleId(moduleId);
    }

    @Transactional
    public List<Unit> getAllUnits() {
        
       return unitRepository.findAll();
    }

  
}
