package com.geeks4learning.CourseGen.Entities;

import jakarta.persistence.*;
import lombok.*;

@AllArgsConstructor
@NoArgsConstructor

@Data
@Entity
@Table(name = "Activity")
public class Activity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "activity_id")
    private Long activityId;

    @Column(name = "activity_name", columnDefinition = "TEXT")
    private String activityName;

    @Column(name = "duration")
    private int duration;

    @Column(name = "instructions", columnDefinition = "TEXT")
    private String instructions;

    @ManyToOne
    @JoinColumn(name = "unit_id")
    private Unit unit;

    public Activity(String activityName, Unit unit) {
        this.activityName = activityName;
        this.unit = unit;
    }


}
