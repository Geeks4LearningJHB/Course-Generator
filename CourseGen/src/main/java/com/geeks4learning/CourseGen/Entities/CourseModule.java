package com.geeks4learning.CourseGen.Entities;

import java.util.*;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.*;

import com.fasterxml.jackson.annotation.JsonIgnore;


import lombok.*;

@AllArgsConstructor
@NoArgsConstructor

@Data
@Document(collection = "Module")
public class CourseModule {

    @Id
    private String moduleId;

    private String moduleName;

    private String moduleDescription;

    private String duration;

    @DBRef
    private List<Unit> units = new ArrayList<>();

    
}
