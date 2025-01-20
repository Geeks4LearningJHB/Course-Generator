import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class GenerateContentService {
  private apiUrl = 'http://localhost:8080/AI/';
  private generatedCourse: any;

  constructor(private http: HttpClient) {}

  // Method to generate the course
  generateCourse(data: { courseTitle: string; difficulty: string; duration: number }): Observable<any> {
    const { difficulty, duration } = data;
    return this.http.post(`${this.apiUrl}generateCourse`, data);
  }

  // Method to save the generated course, including units
  saveGeneratedCourse(generatedCourseData: any): Observable<any> {
    const courseId = generatedCourseData.courseId || generatedCourseData.id;
    const params = new HttpParams().set('courseId', courseId);

    // Assuming units are part of the generatedCourseData
    const units = this.getUnitsFromMemory();

    return this.http.post(`http://localhost:8080/AI/saveGeneratedCourse`, { 
      courseId: courseId,
      units: units  // Include the units from memory
    }, { 
      params: params,
      responseType: 'text'
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Method to set the generated course, including units
  setGeneratedCourse(course: any): void {
    this.generatedCourse = course;
  }

  // Method to get the generated course
  getGeneratedCourse(): any {
    return this.generatedCourse;
  }

  // Method to get the units from the generated course stored in memory
  getUnitsFromMemory(): any[] {
    return this.generatedCourse?.units || [];
  }

  // Clear the stored course and its units from memory
  clearGeneratedCourse(): void {
    this.generatedCourse = null;
  }

  // Error handling method
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An error occurred';
    if (error.error instanceof ErrorEvent) {
      errorMessage = error.error.message;
    } else {
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
