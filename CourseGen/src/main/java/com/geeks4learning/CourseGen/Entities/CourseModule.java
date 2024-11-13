package com.geeks4learning.CourseGen.Entities;

import java.util.*;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;
import lombok.*;

@AllArgsConstructor
@NoArgsConstructor

@Data
@Entity
@Table(name = "Module")
public class CourseModule {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "module_id")
    private Long moduleId;

    @Column(name = "module_name", columnDefinition = "TEXT")
    private String moduleName;

 
    @Column(name = "module_description", columnDefinition = "TEXT")
    private String moduleDescription;

    @Column(name = "duration", columnDefinition = "TEXT")
    private String duration;

    @OneToMany(mappedBy = "module", cascade = CascadeType.ALL)
    private List<Unit> units = new ArrayList<>();

    public CourseModule(String moduleName, String moduleDescription, String duration) {
        this.moduleName = moduleName;
        this.moduleDescription = moduleDescription;
        this.duration = duration;
    }
}
