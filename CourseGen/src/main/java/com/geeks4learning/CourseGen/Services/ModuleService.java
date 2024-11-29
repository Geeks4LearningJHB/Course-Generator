package com.geeks4learning.CourseGen.Services;

import java.util.*;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.geeks4learning.CourseGen.DTOs.CourseModuleDTO;
import com.geeks4learning.CourseGen.Entities.CourseModule;
import com.geeks4learning.CourseGen.Repositories.ModuleRepository;


@Service
public class ModuleService {

    @Autowired
    private ModuleRepository moduleRepository;

    @Autowired
    private UnitService unitService;

    public CourseModule saveModule(CourseModule module) {
        return moduleRepository.save(module);
    }

    public Optional<CourseModule> findCourseModuleById(String id) {
        return moduleRepository.findById(id);
    }

    public List<CourseModule> findAllModules() {
        return moduleRepository.findAll();
    }

    public List<CourseModule> findModuleByName(String search) {
        return moduleRepository.findByModuleName(search);
    }

// public List<CourseModuleDTO> convertModulesToDTO(List<CourseModule> modules) {
//     return modules.stream()
//                   .map(this::convertToDTO)
//                   .collect(Collectors.toList());
// }

// // Conversion helper for CourseModule to CourseModuleDTO
// private CourseModuleDTO convertToDTO(CourseModule module) {
//     return new CourseModuleDTO(
//         module.getModuleId(),
//         module.getModuleName(),
//         module.getModuleDescription(),
//         module.getDuration(),
//         unitService.convertUnitsToDTO(module.getUnits()));
// }
    
}
