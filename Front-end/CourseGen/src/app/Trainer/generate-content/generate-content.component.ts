import { Component } from '@angular/core';

@Component({
  selector: 'app-generate-content',
  templateUrl: './generate-content.component.html',
  styleUrl: './generate-content.component.css'
})
export class GenerateContentComponent {
  courseTitle: string = '';
  difficulty: string = 'Beginner';
  duration: number | null = null;

  onGenerateCourse() {
    console.log('Course Title:', this.courseTitle);
    console.log('Difficulty:', this.difficulty);
    console.log('Duration:', this.duration);
    alert(`Course "${this.courseTitle}" generated successfully!`);
  }
  isLoading = false;
  isComplete = false;
  countdown = 30; // Initial countdown in minutes
  generatedData: string = ''; // Placeholder for backend data

  startGeneration() {
    this.isLoading = true;
    this.isComplete = false;
    this.countdown = 30;

    // Start countdown timer
    const interval = setInterval(() => {
      this.countdown--;
      if (this.countdown <= 0) {
        clearInterval(interval);
        this.completeGeneration();
      }
    }, 60000); // Updates every minute

    // Simulate fetching data from the backend
    setTimeout(() => {
      this.generatedData = "Generated course content from backend.";
    }, 1800000); // Simulates a 30-minute backend process
  }

  completeGeneration() {
    this.isLoading = false;
    this.isComplete = true;
  }
}