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
  showOutlineModal = false; // Show/hide outline modal
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

    // Fetch and display course outline first
    this.onGenerateOutline();
  }

  // Fetch course outline and display in modal
  onGenerateOutline() {
    const outlineData = {
      prompt: this.courseTitle,
      difficulty: this.difficulty,
      duration: this.duration ?? 0
    };

    this.generateContentService.getOutline(outlineData).subscribe(
      (response: any) => {
        this.courseOutline = response.outline; // Assuming `outline` is part of the response
        this.showOutlineModal = true; // Open modal
      },
      (error: HttpErrorResponse) => {
        console.error('Error fetching course outline:', error);
        alert('Failed to fetch course outline.');
      }
    );
  }

  // Confirm course generation after viewing the outline
  confirmCourseGeneration() {
    this.showOutlineModal = false; // Close modal
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
        this.router.navigate(['/view-content']);
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
