package com.geeks4learning.CourseGen.DTOs;

import com.geeks4learning.CourseGen.Model.CourseRequest;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class PromtDTO {

    private String promt;
    private String difficulty;
    private int duration;

    public PromtDTO(CourseRequest courseRequest) {
        this.promt = courseRequest.getCourseTitle();
        this.difficulty = courseRequest.getDifficulty();
        this.duration = courseRequest.getDuration();
    }
}
