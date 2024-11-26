package com.geeks4learning.CourseGen.DTOs;

import java.util.ArrayList;
import java.util.List;

public class CourseNode {
    
     private String title;
    private String content;  // Detailed content for Units
    private List<CourseNode> children = new ArrayList<>();

    // Constructor
    public CourseNode(String title) {
        this.title = title;
    }

    // Getters and Setters
    public String getTitle() {
        return title;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public List<CourseNode> getChildren() {
        return children;
    }

    public void addChild(CourseNode child) {
        this.children.add(child);
    }
    
}
