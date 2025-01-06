import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GenerateContentService {
  saveCourse(generatedCourse: any) {
    throw new Error('Method not implemented.');
  }

  private apiUrl = 'http://localhost:8080/AI/generateCourse';
  private generatedCourse: any; // Temporary storage for the generated course

  constructor(private http: HttpClient) {}

  generateCourse(data: { courseTitle: string; difficulty: string; duration: number }): Observable<any> {
    // Access difficulty and duration from the data object to construct the URL
    const { difficulty, duration } = data;

    // Use query parameters in the URL and send 'data' as the request body
    return this.http.post(`http://localhost:8080/AI/generateCourse`, data);
  }



  getOutline(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}`, data); // Update with your backend endpoint
  }
  // http://localhost:8080/AI/saveGeneratedCourse

  saveGeneratedCourse(courseData: any): Observable<any> {
    return this.http.post('http://localhost:8080/AI/saveGeneratedCourse', courseData);
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
