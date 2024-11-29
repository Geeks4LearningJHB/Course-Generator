package com.geeks4learning.CourseGen.DTOs;

import java.util.*;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class CourseModuleDTO {

    private String moduleName;
    private String moduleDescription;
    private String duration;
    private List<UnitDTO> units;
}
