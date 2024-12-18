import { Component, HostListener } from '@angular/core';
import { GenerateContentService } from '../../Services/generate-content.service'; // Adjust import path as needed
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-generate-content',
  templateUrl: './generate-content.component.html',
  styleUrls: ['./generate-content.component.css']
})
export class GenerateContentComponent {
  courseTitle: string = '';
  difficulty: string = 'Beginner';
  duration: number | null = null;
  isCollapsed = true;
  progress = 0;
  isLoading = false;
  courseOutline: string = ''; // Store course outline

  constructor(
    private router: Router,
    private generateContentService: GenerateContentService
  ) {}

  // Triggered when the form is submitted
  onGenerateCourse() {
    if (!this.courseTitle || !this.difficulty || this.duration == null) {
      alert('Please fill in all fields.');
      return;
    }

    this.isLoading = true;

    const courseData = {
      prompt: this.courseTitle,
      difficulty: this.difficulty,
      duration: this.duration ?? 0
    };

    // Call the backend API to generate the course dynamically
    this.generateContentService.generateCourse(courseData).subscribe(
      (response: any) => {
        // Store the generated course data in the service
        this.generateContentService.setGeneratedCourse(response);

        this.isLoading = false;

        // Navigate to the view page to show the generated course
        this.router.navigate(['/view-generated-course']);
      },
      (error: HttpErrorResponse) => {
        console.error('Error generating course:', error);
        this.isLoading = false;
        alert('Failed to generate course.');
      }
    );
  }

  // Confirm course generation after viewing the outline
  confirmCourseGeneration() {
    
    this.isLoading = true; // Start loading process
    this.progress = 0;

    const courseData = {
      prompt: this.courseTitle,
      difficulty: this.difficulty,
      duration: this.duration ?? 0
    };

    this.generateContentService.generateCourse(courseData).subscribe(
      (response: any) => {
        this.isLoading = false;
        this.progress = 100;

        // Navigate to view content
        this.router.navigate(['/course-save-component']);
      },
      (error: HttpErrorResponse) => {
        console.error('Error generating course:', error);
        this.isLoading = false;
        alert('Failed to generate course.');
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
