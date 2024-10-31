package com.geeks4learning.CourseGen.Model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class CourseRequest {
    private String courseTitle;
    private String difficulty;
    private Integer duration;
}
