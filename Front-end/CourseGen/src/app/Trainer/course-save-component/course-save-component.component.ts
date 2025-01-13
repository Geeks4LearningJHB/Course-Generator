import { Component, HostListener, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { GenerateContentService } from '../../Services/generate-content.service';

@Component({
  selector: 'app-course-save-component',
  template: `
    <div class="main-content" [class.shifted]="!isCollapsed">
      <button class="toggle-btn" (click)="toggleSidebar()">
        ☰
      </button>

      <div class="content-area">
        <div *ngIf="successMessage" class="alert alert-success">
          {{ successMessage }}
        </div>
        <div *ngIf="errorMessage" class="alert alert-danger">
          {{ errorMessage }}
        </div>

        <div class="course-details">
          <h2>{{ moduleName }}</h2>
          <p>Duration: {{ duration }} hours</p>
          <p>Difficulty: {{ difficulty }}</p>
          <p>Course Outline: {{ courseOutline }}</p>
        </div>

        <button 
          (click)="onSaveCourse()"
          [disabled]="isLoading || !generatedCourseData"
          class="save-btn">
          {{ isLoading ? 'Saving...' : 'Save Course' }}
        </button>
      </div>
    </div>
  `
})
export class CourseSaveComponent implements OnInit {
  isCollapsed = true;
  isLoading = false;
  successMessage = '';
  errorMessage = '';

  courseOutline: string = '';
  duration: number = 0;
  difficulty: string = '';
  moduleName: string = '';
  generatedCourseData: any;

  constructor(
    private route: ActivatedRoute,
    private generateContentService: GenerateContentService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadRouteData();
  }

  private loadRouteData(): void {
    try {
      this.moduleName = this.route.snapshot.queryParamMap.get('title') ?? '';
      this.difficulty = this.route.snapshot.queryParamMap.get('difficulty') ?? '';
      this.duration = +(this.route.snapshot.queryParamMap.get('duration') ?? '0');
      this.courseOutline = this.route.snapshot.queryParamMap.get('outline') ?? '';
      
      // Get generated course data from history state
      this.generatedCourseData = history.state.generatedCourseData;

      if (!this.generatedCourseData) {
        this.errorMessage = 'No course data available. Please generate course content first.';
        return;
      }

      // Log the courseId to verify it's available
      console.log('Course ID:', this.generatedCourseData.courseId || this.generatedCourseData.id);

    } catch (error) {
      this.errorMessage = 'Error loading course data. Please try again.';
      console.error('Error in loadRouteData:', error);
    }
  }

  onSaveCourse(): void {
    if (!this.generatedCourseData) {
      this.errorMessage = 'No course data available to save.';
      return;
    }

    // Verify courseId exists
    const courseId = this.generatedCourseData.courseId || this.generatedCourseData.id;
    if (!courseId) {
      this.errorMessage = 'Course ID not found in generated data.';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.generateContentService.saveGeneratedCourse(this.generatedCourseData)
      .subscribe({
        next: (response) => {
          this.successMessage = 'Course saved successfully!';
          this.isLoading = false;
          
          // Navigate after showing success message
          setTimeout(() => {
            this.router.navigate(['/view-content'], { 
              queryParams: { 
                saved: true,
                courseId: courseId
              }
            });
          }, 1500);
        },
        error: (error) => {
          this.isLoading = false;
          this.errorMessage = error.error?.message || 'Error saving course. Please try again.';
          console.error('Error saving course:', error);
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