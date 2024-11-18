package com.geeks4learning.CourseGen.DTOs;

import java.util.*;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class CourseModuleDTO {

    public CourseModuleDTO(Long moduleId, String moduleName, String moduleDescription, String duration, List<UnitDTO> units) {
        
        this.moduleName = moduleName;
        this.moduleDescription = moduleDescription;
        this.duration = duration;
        this.units = units;
    }
    private String moduleName;
    private String moduleDescription;
    private String duration;
    private List<UnitDTO> units;
}
