package com.geeks4learning.CourseGen.Entities;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.DBRef;
import org.springframework.data.mongodb.core.mapping.Document;

import com.fasterxml.jackson.annotation.JsonIgnore;

import lombok.*;


@AllArgsConstructor
@NoArgsConstructor

@Data
@Document(collection = "Assessment")
public class Assessment {

    @Id
    private String assessmentId;

    private String assessmentName;

    private int duration;

    @DBRef
    @JsonIgnore
    private Unit unit;

}
