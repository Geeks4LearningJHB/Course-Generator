/* import { Component, HostListener } from '@angular/core';
import { GenerateContentService } from '../../Services/generate-content.service';
import { Router } from '@angular/router';
import { ToggleService } from '../../Services/toggle.service';


@Component({
  selector: 'app-generate-content',
  templateUrl: './generate-content.component.html',
  styleUrls: ['./generate-content.component.css']
})
export class GenerateContentComponent {
  courseTitle: string = '';
  difficulty: string = 'beginner';
  duration: number | null = null;
  isCollapsed = true;
  isLoading = false;
  courseOutline: string = '';

  constructor(
    private router: Router,
    private generateContentService: GenerateContentService,
    private toggleService: ToggleService
  ) {}

  private getCourseData() {
    return {
      topic: this.courseTitle,
      level: this.difficulty.toLowerCase(),
      save_to_db: false
    };
  }

  onGenerateCourse() {
    if (!this.courseTitle || !this.difficulty || this.duration == null) {
      alert('Please fill in all fields.');
      return;
    }

    this.isLoading = true;

    // ✅ Dummy course response
    const dummyResponse = {
      title: this.courseTitle,
      level: this.difficulty,
      duration: this.duration,
      modules: [
        {
          title: 'Module 1: Introduction',
          units: [
            { title: 'Unit 1.1: Welcome', content: 'Welcome to the dummy course.' },
            { title: 'Unit 1.2: Setup', content: 'Here is how you get started.' }
          ]
        },
        {
          title: 'Module 2: Basics',
          units: [
            { title: 'Unit 2.1: Concepts', content: 'Core concepts explained.' },
            { title: 'Unit 2.2: Examples', content: 'Basic examples to try out.' }
          ]
        }
      ]
    };

    this.generateContentService.setGeneratedCourse(dummyResponse);
    this.isLoading = false;
    this.router.navigate(['/view-generated-course']);
  }

  confirmCourseGeneration() {
    this.isLoading = true;

    // ✅ Dummy course response reused
    const dummyResponse = {
  title: 'Python Course for Beginners',
  modules: [
    {
      title: 'Module 1: Introduction',
      units: [
        {
          title: 'What is Python?',
          explanation: 'Python is a high-level, interpreted programming language...',
          examples: ['print("Hello, world!")'],
          resources: ['https://docs.python.org/3/'],
          order: 1
        },
        {
          title: 'Where is Python?',
          explanation: 'Python is a high-level, interpreted programming language...',
          examples: ['print("Hello, world!")'],
          resources: ['https://docs.python.org/3/'],
          order: 2
        }
      ]
    }
  ]
};

    this.generateContentService.setGeneratedCourse(dummyResponse);
    this.isLoading = false;
    this.router.navigate(['/view-generated-course']);
  }

  ngOnInit(): void {
    this.toggleService.isCollapsed$.subscribe(
      (collapsed) => (this.isCollapsed = collapsed)
    );
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.sidebar') && !target.closest('.toggle-btn')) {
      this.isCollapsed = true;
    }
  }
} */



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
  difficulty: string = 'beginner';
  duration: number | null = null;
  isCollapsed = true;
  isLoading = false;
  courseOutline: string = '';

  constructor(
    private router: Router,
    private generateContentService: GenerateContentService,
    private toggleService: ToggleService
  ) {}

  // 🔁 Helper to prepare course data
  private getCourseData() {
    return {
      topic: this.courseTitle,
      level: this.difficulty.toLowerCase(),
      save_to_db: false
    };
  }

  // Triggered when the form is submitted
  onGenerateCourse() {
    if (!this.courseTitle || !this.difficulty || this.duration == null) {
      alert('Please fill in all fields.');
      return;
    }

    this.isLoading = true;

    const courseData = this.getCourseData();

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

  ngOnInit(): void {
    this.toggleService.isCollapsed$.subscribe(
      (collapsed) => (this.isCollapsed = collapsed)
    );
  }

  confirmCourseGeneration() {
    this.isLoading = true;

    const courseData = this.getCourseData();

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

  // toggleSidebar() {
  //   this.isCollapsed = !this.isCollapsed;
  // }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.sidebar') && !target.closest('.toggle-btn')) {
      this.isCollapsed = true;
    }
  }
}