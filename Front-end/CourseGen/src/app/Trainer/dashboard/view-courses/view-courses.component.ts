import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-view-courses',
  templateUrl: './view-courses.component.html',
  styleUrl: './view-courses.component.css'
})
export class ViewCoursesComponent {
  constructor(private router: Router) {}

  openViewContent() {
    this.router.navigate(['/view-content']); // Use the path defined in your routes
  }
}
