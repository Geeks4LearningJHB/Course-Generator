import { Component, HostListener } from '@angular/core';
import { GenerateContentService } from '../../Services/generate-content.service';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { ToggleService } from '../../Services/toggle.service';

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
  isLoading = false;
  courseOutline: string = '';

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
      courseTitle: this.courseTitle,
      difficulty: this.difficulty,
      duration: this.duration ?? 0
    };

    this.generateContentService.generateCourse(courseData).subscribe({
      next: (response: any) => {
        this.generateContentService.setGeneratedCourse(response);
        this.isLoading = false;
        this.router.navigate(['/view-generated-course']);
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error generating course:', error);
        this.isLoading = false;
        alert('Failed to generate course.');
      }
    });
  }

  confirmCourseGeneration() {
    this.isLoading = true;

    const courseData = {
      courseTitle: this.courseTitle,
      difficulty: this.difficulty,
      duration: this.duration ?? 0
    };

    this.generateContentService.generateCourse(courseData).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        this.router.navigate(['/course-save-component']);
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error generating course:', error);
        this.isLoading = false;
        alert('Failed to generate course.');
      }
    });
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