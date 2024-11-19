package com.geeks4learning.CourseGen.Entities;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor

@Data
@Document(collection = "Promt")
public class Promt {

    @Id
    private String promtId;

    private String promt;

    private String difficulty;

    private int duration;

}
