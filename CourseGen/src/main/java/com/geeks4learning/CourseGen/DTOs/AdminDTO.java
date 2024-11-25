package com.geeks4learning.CourseGen.DTOs;


import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class AdminDTO {

    private String Name;
    private String Surname;
    private String email;
    private String password;
}
