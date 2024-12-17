package com.geeks4learning.CourseGen.Services;

import java.util.*;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.*;

import com.geeks4learning.CourseGen.Entities.CourseModule;
import com.geeks4learning.CourseGen.Entities.Outline;
import com.geeks4learning.CourseGen.Repositories.OutlineRepository;

@Service
public class OutlineService {

    @Autowired
    private OutlineRepository outlineRepository;

    public Outline saveOutline(Outline outline){
        return outlineRepository.save(outline);
    }

    public Optional<Outline> findOutlineById(String id) {
        return outlineRepository.findById(id);
    }
}
