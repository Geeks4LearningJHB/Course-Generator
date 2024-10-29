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
}