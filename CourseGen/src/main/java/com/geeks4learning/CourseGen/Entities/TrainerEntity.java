package com.geeks4learning.CourseGen.Entities;

//import Trainer.Status;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@AllArgsConstructor
@NoArgsConstructor

@Data
@Entity
@Table(name = "Trainer")
public class TrainerEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "UserId")
    private long UserId;

    @Column(name = "Name")
    private String Name;

    @Column(name = "Surname")
    private String Surname;

    @Column(name = "Email")
    private String email;

    @Column(name = "Password")
    private String password;

    @Column(nullable = false)
    private String status = "pending";

    public void setName(String name) {
        this.Name = name;
    }

    public void setSurname(String surname) {
        this.Surname = surname;
    }
}
