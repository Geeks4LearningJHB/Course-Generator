import { Component,   HostListener } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-admin-generate-content',
  templateUrl: './admin-generate-content.component.html',
  styleUrl: './admin-generate-content.component.css'
})
export class AdminGenerateContentComponent {

  courseTitle: string = '';
  difficulty: string = 'Beginner';
  duration: number | null = null;
  isCollapsed = true;

  onGenerateCourse() {
    console.log('Course Title:', this.courseTitle);
    console.log('Difficulty:', this.difficulty);
    console.log('Duration:', this.duration);
    alert(`Course "${this.courseTitle}" generated successfully!`);
  }
  isLoading = false;
  isComplete = false;
  countdown = 30;
  generatedData: string = ''; 

  startGeneration() {
    this.isLoading = true;
    this.isComplete = false;
    this.countdown = 1;

    const interval = setInterval(() => {
      this.countdown--;
      if (this.countdown <= 0) {
        clearInterval(interval);
        this.completeGeneration();
      }
    }, 2000); 
   
    setTimeout(() => {
      this.generatedData = "Generated course content from backend with extensive information...Generated course content from backend with extensive information...Generated course content from backend with extensive information...Generated course content from backend with extensive information...Generated course content from backend with extensive information...";
    }, 18000); 
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
