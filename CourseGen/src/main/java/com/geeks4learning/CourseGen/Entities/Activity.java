package com.geeks4learning.CourseGen.Entities;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.DBRef;
import org.springframework.data.mongodb.core.mapping.Document;

import com.fasterxml.jackson.annotation.JsonIgnore;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Data
@Document(collection = "activities")
public class Activity {

    @Id
    private String activityId;

    private String activityName;

    private int duration;

    private String instructions;

    @DBRef
    @JsonIgnore
    private Unit unit;

    public Activity(String activityName, Unit unit) {
        this.activityName = activityName;
        this.unit = unit;
    }
}
