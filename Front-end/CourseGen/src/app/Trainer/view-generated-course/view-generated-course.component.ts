import { Component, HostListener } from '@angular/core';
import { GenerateContentService } from '../../Services/generate-content.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-view-generated-course',
  templateUrl: './view-generated-course.component.html',
  styleUrl: './view-generated-course.component.css'
})
export class ViewGeneratedCourseComponent {
  generatedCourse: any = null;
  isCollapsed = true;

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

  goBack() {
    window.history.back();
  }
  
  // Save course (can be extended to send data to the backend)
  saveCourse() {
    // Call API to save the course to the database
    this.generateContentService.saveGeneratedCourse(this.generatedCourse).subscribe(
      (response) => {
        alert('Course saved successfully!');
        this.router.navigate(['/dashboard']);
      },
      (error) => {
        alert('Failed to save course.');
      }
    );
  }

    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
    }
  
    @HostListener('document:click', ['$event'])
    onDocumentClick(event: MouseEvent) {
      const target = event.target as HTMLElement;
  
      if (!target.closest('.sidebar') && !target.closest('.toggle-btn')) {
        this.isCollapsed = true;
      }
    }

}
