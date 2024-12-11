import { Component, HostListener, OnInit } from '@angular/core';
import { Unit, ViewContentService } from '../../Services/view-content.service';
import { Course, ViewCoursesService,  } from '../../Services/view-courses.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-view-content',
  templateUrl: './view-content.component.html',
  styleUrl: './view-content.component.css'
})
export class ViewContentComponent implements OnInit{
  showModifyFields: boolean = false;
  module: string = '';
  topic: string = '';
  details: string = '';
  isCollapsed = true;
  units: Unit[] = [];
  courses: Course[] = [];
  selectedCourse: Course | null = null;
  generatedData: any;

  constructor(private router: Router, private viewContentService: ViewContentService, private viewCoursesService: ViewCoursesService) {
    const nav = this.router.getCurrentNavigation();
    this.generatedData = nav?.extras.state?.['data'];
  }

  ngOnInit(): void {
    this.viewContentService.getAllUnits().subscribe({
      next: (data) => {
        this.units = data.map((unit) => ({ ...unit, isExpanded: false })); // Initialize isExpanded to false
      },
      error: (err) => console.error('Error fetching units', err)
    });

    this.viewCoursesService.getCourses().subscribe({
      next: (data) => {
        this.courses = data;
        console.log('Fetched courses:', this.courses); // Debugging
        if (this.courses.length > 0) {
          this.selectedCourse = null; // Ensure no course is pre-selected
        }
      },
      error: (err) => console.error('Error fetching courses', err),
    });

    if (!this.generatedData) {
      console.error('No generated data found');
    }
  }

  toggleUnit(unit: any): void {
    unit.isExpanded = !unit.isExpanded; // Toggle expanded state
  }
  
  
  onModifyContent() {
    console.log('Module:', this.module);
    console.log('Topic:', this.topic);
    console.log('Details:', this.details);
    alert('Content modified successfully!');
    this.module = '';
    this.topic = '';
    this.details = '';
  }

  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }

  onCourseSelect(course: Course): void {
    console.log('Course selected:', course); // Check selected course
    this.selectedCourse = course; // Update the selected course
  
    this.viewContentService.getUnitsByModules(this.selectedCourse.id).subscribe({
      next: (data) => {
        console.log('Fetched units for selected course:', data); // Debugging units response
        this.units = data.map((unit) => ({ ...unit, isExpanded: false })); // Set units
      },
      error: (err) => console.error('Error fetching units for selected course:', err),
    });
  }
  
}
