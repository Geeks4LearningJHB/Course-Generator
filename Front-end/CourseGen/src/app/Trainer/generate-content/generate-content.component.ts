import { Component, HostListener } from '@angular/core';
import { GenerateContentService } from '../../Services/generate-content.service';  // Adjust import path as needed

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
  isComplete = false;
  countdown = 30; // Initial countdown in minutes
  generatedData: string = ''; // Placeholder for backend data

  constructor(private generateContentService: GenerateContentService) {}

  onGenerateCourse() {
    console.log('Course Title:', this.courseTitle);
    console.log('Difficulty:', this.difficulty);
    console.log('Duration:', this.duration);
    alert(`Course "${this.courseTitle}" generated successfully!`);

    // Call backend API to generate course content
    this.startGeneration();
  }

  startGeneration() {
    this.isLoading = true;
    this.isComplete = false;
    this.countdown = 1;
  
    // Start countdown timer
    const interval = setInterval(() => {
      this.countdown--;
      if (this.countdown <= 0) {
        clearInterval(interval);
        this.completeGeneration();
      }
    }, 2000); // Updates every 2 seconds
  
    // Ensure that duration is always a number
    const courseData = {
      courseTitle: this.courseTitle,
      difficulty: this.difficulty,
      duration: this.duration ?? 0  // Convert null to 0 if duration is null
    };
  
    this.generateContentService.generateCourse(courseData).subscribe(
      (response: any) => {
        this.generatedData = response;  // Update with the actual generated data
      },
      (error) => {
        console.error('Error generating course content:', error);
        this.isLoading = false;
      }
    );
  
  
  }

  completeGeneration() {
    this.isLoading = false;
    this.isComplete = true;
  }

  closeModal() {
    this.isComplete = false;
  }

  onSave() {
    alert('Course content saved successfully!');
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
