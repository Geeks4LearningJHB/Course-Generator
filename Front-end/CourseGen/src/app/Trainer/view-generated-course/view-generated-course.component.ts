import { Component } from '@angular/core';
import { GenerateContentService } from '../../Services/generate-content.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-view-generated-course',
  templateUrl: './view-generated-course.component.html',
  styleUrl: './view-generated-course.component.css'
})
export class ViewGeneratedCourseComponent {
  generatedCourse: any = null;

  constructor(
    private router: Router,
    private generateContentService: GenerateContentService
  ) {}

  ngOnInit() {
    // Retrieve the generated course from the service
    this.generatedCourse = this.generateContentService.getGeneratedCourse();

    if (!this.generatedCourse) {
      alert('No course has been generated.');
      this.router.navigate(['/generate-content']); // Redirect if no course is found
    }
  }

  // Navigate back to generate content
  onEditCourse() {
    this.router.navigate(['/generate-content']);
  }

  // Save course (can be extended to send data to the backend)
  onSaveCourse() {
    alert('Course saved successfully!');
    this.generateContentService.clearGeneratedCourse();
    this.router.navigate(['/dashboard']); // Redirect to dashboard or another page
  }

}
