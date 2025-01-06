package com.geeks4learning.CourseGen.DTOs;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class HighlightRequestDTO {
    private String unitId;
    private String moduleId;
    private String highlightedText;
}
