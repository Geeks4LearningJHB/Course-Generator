package com.geeks4learning.CourseGen.DTOs;

import lombok.*;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class UnitDTO {

    private Long unitId;
    private String unitName;
    private String unitDescription;
    private int duration;
    private String content;
    private int unitNum;;
   
    
}