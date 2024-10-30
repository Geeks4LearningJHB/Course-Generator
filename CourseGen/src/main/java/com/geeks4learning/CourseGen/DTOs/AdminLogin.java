package com.geeks4learning.CourseGen.DTOs;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class AdminLogin {
    private String Email;
    private String Password;
}
