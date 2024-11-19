package com.geeks4learning.CourseGen.Entities;

import lombok.*;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.DBRef;

import java.util.List;

@AllArgsConstructor
@NoArgsConstructor
@Data
@Document(collection = "units")
public class Unit {

    @Id
    private String unitId; // MongoDB uses String (ObjectId) for IDs

    private String unitName;

    private String unitDescription;

    private int unitNum;

    private String content;

    private int duration;

    @DBRef
    private CourseModule module; // Reference to another collection

    @DBRef
    private List<Assessment> assessmentUnits; // References to assessments

    @DBRef
    private List<Activity> activityUnits; // References to activities

    
}
