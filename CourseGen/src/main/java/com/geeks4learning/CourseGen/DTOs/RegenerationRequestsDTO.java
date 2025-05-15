package com.geeks4learning.CourseGen.DTOs;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class RegenerationRequestsDTO {

    private String moduleId;
    private String unitId;
    private String reason;
}
