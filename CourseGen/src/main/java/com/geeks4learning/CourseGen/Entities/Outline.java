package com.geeks4learning.CourseGen.Entities;

import java.util.*;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.*;

import com.fasterxml.jackson.annotation.*;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor

@Data
@Document(collection = "Outline")
public class Outline {

    @Id
    private String outlineId;

    private String outlineName;

    @DBRef
    @JsonIgnore
    private CourseModule module;

    @DBRef
    @JsonIgnore
    private List<Unit> units;
}
