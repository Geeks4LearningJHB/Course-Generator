package com.geeks4learning.CourseGen.Entities;

import lombok.*;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.ElementCollection;

import org.springframework.data.mongodb.core.mapping.DBRef;

import java.util.ArrayList;
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

    @ElementCollection
private List<String> highlightedSections; // Stores highlighted sections


    @DBRef
    @JsonIgnore
    private CourseModule module; // Reference to another collection

    @DBRef
    @JsonIgnore
    private List<Assessment> assessmentUnits = new ArrayList<>(); // Initialize to avoid null issues

    @DBRef
    @JsonIgnore
    private List<Activity> activityUnits = new ArrayList<>(); // Initialize to avoid null issues

    public Unit(CourseModule module) {
        this.module = module;
        this.assessmentUnits = new ArrayList<>();
        this.activityUnits = new ArrayList<>();
    }
}
