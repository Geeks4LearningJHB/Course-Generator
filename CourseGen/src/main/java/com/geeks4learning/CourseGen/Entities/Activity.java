package com.geeks4learning.CourseGen.Entities;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.DBRef;
import org.springframework.data.mongodb.core.mapping.Document;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Data
@Document(collection = "activities") // Consistent naming (lowercase, plural)
public class Activity {

    @Id
    private String activityId; // MongoDB ObjectId as String

    private String activityName;

    private int duration;

    private String instructions;

    @DBRef
    private Unit unit; // Reference to the Unit collection
}
