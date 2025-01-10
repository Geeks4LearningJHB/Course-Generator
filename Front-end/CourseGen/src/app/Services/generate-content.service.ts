import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GenerateContentService {

  private apiUrl = 'http://localhost:8080/AI/';
  private generatedCourse: any;

  constructor(private http: HttpClient) {}

  generateCourse(data: { courseTitle: string; difficulty: string; duration: number }): Observable<any> {
    const { difficulty, duration } = data;
    return this.http.post(`${this.apiUrl}generateCourse`, data);
  }

  saveGeneratedCourse(courseData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}saveGeneratedCourse?courseId=${courseData}`, courseData);
    // http://localhost:8080/AI/saveGeneratedCourse?courseId=5171dc23-a14f-4bcc-8107-617e799c34e9
  }
  
  // Set the generated course
  setGeneratedCourse(course: any): void {
    this.generatedCourse = course;
  }

  // Get the generated course
  getGeneratedCourse(): any {
    return this.generatedCourse;
  }

  // Clear the stored course
  clearGeneratedCourse(): void {
    this.generatedCourse = null;
  }
}
