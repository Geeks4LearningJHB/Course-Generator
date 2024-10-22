package com.geeks4learning.CourseGen.DTOs;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class TrainerDTO {
    private String Name;
    private String Surname;
    private String Email;
    private String Password;
}
