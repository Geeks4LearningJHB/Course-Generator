package com.geeks4learning.CourseGen.Services;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.geeks4learning.CourseGen.Entities.Assessment;
import com.geeks4learning.CourseGen.Repositories.assessmentRepository;

@Service
public class AssessmentService {

    @Autowired
    private assessmentRepository assessmentRepository;

    public Assessment saveAssessment(Assessment assessment) {
        return assessmentRepository.save(assessment);
    }

    public List<Assessment> findAssessmentsByModuleId(Long moduleId) {
        return assessmentRepository.findByUnit_Module_ModuleId(moduleId);
    }

    public List<Assessment> getAllAssessments() {
        return assessmentRepository.findAll();
    }
}
