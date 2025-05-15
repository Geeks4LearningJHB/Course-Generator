package com.geeks4learning.CourseGen.Entities;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.HashSet;
import java.util.Set;

@AllArgsConstructor
@NoArgsConstructor
@Data
@Entity
@Table(name = "Trainer")
public class TrainerEntity extends BaseUser {

    @Column(name = "Name", nullable = false)
    private String name;

    @Column(name = "Surname", nullable = false)
    private String surname;

    @Column(nullable = false)
    private String status = "pending";

    @Column(nullable = false, updatable = false)
    private String userType = "Trainer";  

    @Override
    public String getUserType() {
        return this.userType;
    }

    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "trainer_roles",
        joinColumns = @JoinColumn(name = "userId"),
        inverseJoinColumns = @JoinColumn(name = "roleId")
    )
    private Set<Role> roles = new HashSet<>();
}
