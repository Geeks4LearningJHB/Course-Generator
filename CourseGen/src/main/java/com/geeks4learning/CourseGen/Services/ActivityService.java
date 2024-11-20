package com.geeks4learning.CourseGen.Services;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.geeks4learning.CourseGen.Entities.Activity;
import com.geeks4learning.CourseGen.Repositories.activityRepository;

@Service
public class ActivityService {

    @Autowired
    private activityRepository activityRepository;

    public Activity saveActivity(Activity activity) {
        return activityRepository.save(activity);
    }

    public List<Activity> findActivitiesByModuleId(String moduleId) {
        return activityRepository.findByUnit_Module_ModuleId(moduleId);
    }

    public List<Activity> getAllActivities() {
        return activityRepository.findAll();
    }

}
