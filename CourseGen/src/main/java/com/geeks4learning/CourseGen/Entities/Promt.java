package com.geeks4learning.CourseGen.Entities;

import jakarta.persistence.*;
import lombok.*;

@AllArgsConstructor
@NoArgsConstructor

@Data
@Entity
@Table(name = "Promt")
public class Promt {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "promt_id")
    private Long promtId;

    @Column(name = "promt")
    private String promt;

    @Column(name = "difficulty")
    private String difficulty;

    @Column(name = "duration")
    private int duration;

    public Promt(String promt) {
        this.promt = promt;
    }
}
