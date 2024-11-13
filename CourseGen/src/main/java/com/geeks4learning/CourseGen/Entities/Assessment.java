package com.geeks4learning.CourseGen.Entities;

import jakarta.persistence.*;
import lombok.*;


@AllArgsConstructor
@NoArgsConstructor

@Data
@Entity
@Table(name = "Assessment")
public class Assessment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "assessment_id")
    private Long assessmentId;

    @Column(name = "assessment_name", columnDefinition = "TEXT")
    private String assessmentName;

    @Column(name = "duration")
    private int duration;

    @ManyToOne
    @JoinColumn(name = "unit_id")
    private Unit unit;

    public Assessment(String assessmentName, int duration, Unit unit) {
        this.assessmentName = assessmentName;
        this.duration = duration;
        this.unit = unit;
    }
}
