package com.geeks4learning.CourseGen.DTOs;

public class UpdateRequestDTO {
    private String unitId;
    private String regeneratedText;
    private int startIndex;
    private int endIndex;
    
    // Getters and setters
    public String getUnitId() { return unitId; }
    public void setUnitId(String unitId) { this.unitId = unitId; }
    public String getRegeneratedText() { return regeneratedText; }
    public void setRegeneratedText(String regeneratedText) { this.regeneratedText = regeneratedText; }
    public int getStartIndex() { return startIndex; }
    public void setStartIndex(int startIndex) { this.startIndex = startIndex; }
    public int getEndIndex() { return endIndex; }
    public void setEndIndex(int endIndex) { this.endIndex = endIndex; }
}
