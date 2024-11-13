package com.geeks4learning.CourseGen.DTOs;

import lombok.Data;
import lombok.NoArgsConstructor;

//@AllArgsConstructor
@NoArgsConstructor
@Data
public class PromtDTO {

    private String promt;
    private String difficulty;
    private int duration;
    
    public PromtDTO(String prompt, String difficulty, int duration) {
        this.promt = prompt;
        this.difficulty = difficulty;
        this.duration = duration;
    }
    
}
