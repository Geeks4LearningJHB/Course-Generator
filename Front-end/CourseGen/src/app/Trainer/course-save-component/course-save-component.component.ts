import { Component, HostListener, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { GenerateContentService } from '../../Services/generate-content.service';

@Component({
  selector: 'app-course-save-component',
  templateUrl: './course-save-component.component.html',
  styleUrls: ['./course-save-component.component.css']
})
export class CourseSaveComponent implements OnInit {

  isCollapsed = true;
  courseOutline: string = '';
  duration: number = 0;
  difficulty: string = '';
  moduleName: string = '';
  
  generatedCourseData: any;

  constructor(
    private route: ActivatedRoute,
    private generateContentService: GenerateContentService,
    private router: Router // To navigate after saving the course
  ) { }

  ngOnInit(): void {
    // Retrieve data passed via route parameters or resolver
    this.moduleName = this.route.snapshot.queryParamMap.get('title')!;
    this.difficulty = this.route.snapshot.queryParamMap.get('difficulty')!;
    this.duration = +this.route.snapshot.queryParamMap.get('duration')!;
    this.courseOutline = this.route.snapshot.queryParamMap.get('outline')!;
    this.generatedCourseData = history.state.generatedCourseData; // Access state passed during navigation
  }

  // Method to save the course
  onSaveCourse(): void {
    if (this.generatedCourseData) {
      this.generateContentService.saveGeneratedCourse(this.generatedCourseData).subscribe(
        (response) => {
          console.log('Course saved successfully!', response);
          // Navigate to the next page or show a success message
          this.router.navigate(['/view-content'], { queryParams: { saved: true } });
        },
        (error) => {
          console.error('Error saving course', error);
          // Handle error (e.g., show an error message to the user)
        }
      );
    } else {
      console.error('No generated course data available to save.');
    }
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
