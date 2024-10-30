import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  constructor(private router: Router) {}

  navigateToViewCourse() {
    this.router.navigate(['/view-course']); // Use the path defined in your routes
  }

  openGenerateContent() {
    this.router.navigate(['/generate-content']);
  }
}
