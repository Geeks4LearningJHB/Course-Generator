package com.geeks4learning.CourseGen.DTOs;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class PromtDTO {

    private String promt;
    private String difficulty;
    private int duration;
}
