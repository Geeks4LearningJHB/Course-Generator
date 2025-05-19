import { Component, HostListener } from '@angular/core';
import { GenerateContentService } from '../../Services/generate-content.service';
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
  courseResult: any = null;

  constructor(
    private generateContentService: GenerateContentService,
    private toggleService: ToggleService
  ) {}

  ngOnInit(): void {
    this.toggleService.isCollapsed$.subscribe(
      (collapsed) => (this.isCollapsed = collapsed)
    );
  }

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
        this.isLoading = false;
        this.courseResult = response.data; // Store the generated dummy course here
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
      difficulty: this.difficulty.toLowerCase(),
      duration: this.duration ?? 0
    };

    this.generateContentService.generateCourse(courseData).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        // Redirect to the save component if you decide to later
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error generating course:', error);
        this.isLoading = false;
        alert('Failed to generate course.');
      }
    });
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.sidebar') && !target.closest('.toggle-btn')) {
      this.isCollapsed = true;
    }
  }
}
