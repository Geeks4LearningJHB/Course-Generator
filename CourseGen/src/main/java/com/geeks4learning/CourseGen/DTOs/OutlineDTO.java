package com.geeks4learning.CourseGen.DTOs;

import java.util.List;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.DBRef;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.geeks4learning.CourseGen.Entities.CourseModule;
import com.geeks4learning.CourseGen.Entities.Unit;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class OutlineDTO {
    
    private String outlineId;
    private String outlineName;
    private CourseModule module;
    private List<Unit> units;
}
