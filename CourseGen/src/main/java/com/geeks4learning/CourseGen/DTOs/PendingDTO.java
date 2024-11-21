package com.geeks4learning.CourseGen.DTOs;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@NoArgsConstructor
@AllArgsConstructor
@Data
public class PendingDTO {

    private long userId;
    private String Name;
    private String Surname;
    private String Email;

}
