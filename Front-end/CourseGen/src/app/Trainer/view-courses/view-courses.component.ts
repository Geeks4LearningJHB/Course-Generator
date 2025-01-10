import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ViewCoursesService } from '../../Services/view-courses.service';
import { ToggleService } from '../../Services/toggle.service';


@Component({
  selector: 'app-view-courses',
  templateUrl: './view-courses.component.html',
  styleUrl: './view-courses.component.css'
})
export class ViewCoursesComponent implements OnInit {

  isCollapsed = true;
  
  courses: any[] = [];

  constructor(
    private router: Router,
    private viewCoursesService: ViewCoursesService,
    private toggleService: ToggleService) {} // Inject Angular Router

  ngOnInit(): void {
    this.loadCourses();
    this.toggleService.isCollapsed$.subscribe(
      (collapsed) => (this.isCollapsed = collapsed)
    );
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
    // Navigate to view-content and pass the courseId via query parameters
    this.router.navigate(['/view-content'], { queryParams: { id: courseId } });
  }

  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }
}