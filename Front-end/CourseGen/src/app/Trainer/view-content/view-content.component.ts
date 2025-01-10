import { Component, HostListener, OnInit } from '@angular/core';
import { Unit, ViewContentService } from '../../Services/view-content.service';
import { Course, ViewCoursesService,  } from '../../Services/view-courses.service';
import { ActivatedRoute, Router } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
  export interface ListItem {
    text?: string;
    subItems?: string[];
    language?: string;
    code?: string;
  }
  
  export interface ParsedSection {
    heading: string;
    content: string | ListItem[];
  }
  
  export interface ParsedUnit {
    // monthNumber: number;
    title: string;
    introduction: string;
    keyConcepts: string[];
    sections: ParsedSection[];
    isLoaded?: boolean;
  }

  // interface Section {
  //   heading: string;
  //   content: string | string[] | CodeBlock[] | ListItem[];
  // }
  
  // interface CodeBlock {
  //   language: string;
  //   code: string;
  // }
  
  // interface ListItem {
  //   text: string;
  //   subItems?: string[];
  // }
  
  // interface UnitWithState extends Unit {
  //   isExpanded?: boolean;
  //   isLoaded?: boolean;
  // }
  
  // interface UnitContent {
  //   title: string;
  //   introduction: string;
  //   keyConcepts: string[];
  //   sections: Section[];
  //   isLoaded: boolean;
  // }

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
  courseName: string = '';

  constructor(private router: Router, private route: ActivatedRoute, private viewContentService: ViewContentService, private viewCoursesService: ViewCoursesService) {
    const nav = this.router.getCurrentNavigation();
    this.generatedData = nav?.extras.state?.['data'];
  }

  ngOnInit(): void {
       // Get the courseId from the query parameters
       this.route.queryParams.subscribe((params) => {
        const courseId = params['id'];
        if (courseId) {
          this.loadCourseContent(courseId);
        } else {
          console.error('No course ID found in query parameters.');
        }
      });
  }

  loadCourseContent(courseId: string): void {
    this.viewCoursesService.getModuleById(courseId).subscribe({
      next: (course) => {
        this.courseName = course.moduleName; // Assuming course contains moduleName
      },
      error: (err) => console.error('Error fetching course details:', err),
    });
  
    this.viewContentService.getUnitsByModules(courseId).subscribe({
      next: (data) => {
        this.units = data.map((unit) => ({ ...unit, isExpanded: false }));
      },
      error: (err) => console.error('Error fetching course content:', err),
    });
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
  
    this.viewContentService.getUnitsByModules(this.selectedCourse.moduleId).subscribe({
      next: (data) => {
        console.log('Fetched units for selected course:', data); // Debugging units response
        this.units = data.map((unit) => ({ ...unit, isExpanded: false })); // Set units
      },
      error: (err) => console.error('Error fetching units for selected course:', err),
    });
  }
  
}