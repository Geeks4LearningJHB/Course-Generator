package com.geeks4learning.CourseGen.DTOs;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@AllArgsConstructor
@NoArgsConstructor
@Data
public class HighlightRequestDTO {
    private String moduleId;
    private String unitId;
    private String highlightedText;
    private int startIndex;  // Add position tracking
    private int endIndex;    // Add position tracking
    
    // Getters and setters
    public String getModuleId() { return moduleId; }
    public void setModuleId(String moduleId) { this.moduleId = moduleId; }
    public String getUnitId() { return unitId; }
    public void setUnitId(String unitId) { this.unitId = unitId; }
    public String getHighlightedText() { return highlightedText; }
    public void setHighlightedText(String highlightedText) { this.highlightedText = highlightedText; }
    public int getStartIndex() { return startIndex; }
    public void setStartIndex(int startIndex) { this.startIndex = startIndex; }
    public int getEndIndex() { return endIndex; }
    public void setEndIndex(int endIndex) { this.endIndex = endIndex; }
}

