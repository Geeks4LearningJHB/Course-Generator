import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ViewCoursesService } from '../../Services/view-courses.service';


@Component({
  selector: 'app-view-courses',
  templateUrl: './view-courses.component.html',
  styleUrl: './view-courses.component.css'
})
export class ViewCoursesComponent implements OnInit {

  isCollapsed = true;
  
  courses: any[] = [];

  constructor(private router: Router, private viewCoursesService: ViewCoursesService) {} // Inject Angular Router

  ngOnInit(): void {
    this.loadCourses();
  }

  loadCourses(): void {
    this.viewCoursesService.getCourses().subscribe(
      (data) => {
        this.courses = data;
      },
      (error) => {
        console.error('Error fetching courses:', error);
      }
    );
  }

  
  viewCourse(courseId: number) {
    this.router.navigate(['/view-content'], { queryParams: { id: courseId } });
  }
  

  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }
}