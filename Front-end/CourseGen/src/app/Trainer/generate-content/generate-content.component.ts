import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-generate-content',
  templateUrl: './generate-content.component.html',
  styleUrls: ['./generate-content.component.css']
})
export class GenerateContentComponent {
  courseTitle: string = '';
  difficulty: string = 'Beginner';
  duration: number | null = null;
  isLoading = false;
  isComplete = false;
  countdown = 30; // Initial countdown in minutes
  generatedData: string = ''; // Placeholder for backend data

  constructor(private http: HttpClient) {}

  onGenerateCourse() {
    this.startGeneration();
  }

  startGeneration() {
    this.isLoading = true;
    this.isComplete = false;
    this.countdown = 30;

    const courseRequest = {
      courseTitle: this.courseTitle,
      difficulty: this.difficulty,
      duration: this.duration
    };

    // Send the request to the backend
    this.http.post('http://localhost:8080/AI/generateCourse', courseRequest, { responseType: 'text' })
    .subscribe(
        (response: string) => {
            this.generatedData = response; // response should now be valid
            this.isLoading = false;
            this.isComplete = true;
        },
        (error) => {
            console.error('Error generating course:', error);
            this.isLoading = false;
            this.isComplete = true; // End loading on error
        }
    );

    // Start countdown timer
    const interval = setInterval(() => {
      this.countdown--;
      if (this.countdown <= 0) {
        clearInterval(interval);
        this.completeGeneration();
      }
    }, 60000); // Updates every minute
  }

  completeGeneration() {
    this.isLoading = false;
    this.isComplete = true;
  }
}
