import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-admin-view-courses',
  templateUrl: './admin-view-courses.component.html',
  styleUrl: './admin-view-courses.component.css'
})
export class AdminViewCoursesComponent {

  isCollapsed = true;
  
  courses = [
    {
      id: 1,
      title: 'Java Programming for Beginners',
      description: 'This course is designed to introduce the fundamental concepts of object-oriented programming using Java.',
    },
    {
      id: 2,
      title: 'Introduction to Agile Methodology',
      description: 'This course provides an in-depth exploration of Agile methodologies, its values, and collaboration approach in projects.',
    },
    {
      id: 3,
      title: 'Web Services and API Development',
      description: 'This course offers a comprehensive introduction to web services, API technology, and best practices for creating modern applications.',
    },
  ];

  constructor(private router: Router) {} // Inject Angular Router

  viewCourse(courseId: number) {
    // Navigate to view-content and pass the courseId via query parameters
    this.router.navigate(['/view-content'], { queryParams: { id: courseId } });
  }

  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }
}