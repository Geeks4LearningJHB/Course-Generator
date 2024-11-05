package com.geeks4learning.CourseGen.Entities;

import java.util.*;

import jakarta.persistence.*;
import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Data
@Entity
@Table(name = "Units")
public class Unit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "unit_id")
    private Long unitId;

    @Column(name = "unit_name", columnDefinition = "TEXT")
    private String unitName;

    @Column(name = "unit_description", columnDefinition = "TEXT")
    private String unitDescription;

    @Column(name = "unit_num")
    private int unitNum;

    @Lob
    @Column(name = "content", columnDefinition = "TEXT")
    private String content;

    @Column(name = "duration")
    private int duration;

    @ManyToOne(cascade = CascadeType.PERSIST)
    @JoinColumn(name = "module_id", nullable = false)
    private CourseModule module;

    @OneToMany(mappedBy = "unit", cascade = CascadeType.ALL, fetch = FetchType.LAZY) 
    private List<Assessment> assessmentUnits;

    @OneToMany(mappedBy = "unit", cascade = CascadeType.ALL, fetch = FetchType.LAZY) 
    private List<Activity> activityUnits;

    public Unit(String unitName, String content, CourseModule module) {
        this.unitName = unitName;
        this.content = content;
        this.module = module;
    }
}
