import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class GenerateContentService {
  private apiUrl = 'http://localhost:8000/api/course/';
  private generatedCourse: any;

  constructor(private http: HttpClient) {}

  // Method to generate the course
  generateCourse(data: { topic: string; level: string; save_to_db: boolean }): Observable<any> {
    return this.http.post(`${this.apiUrl}generate-course/`, data);
  }
 

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
  if (!this.generatedCourse || !this.generatedCourse.modules) {
    return [];
  }

  const units: any[] = [];

  this.generatedCourse.modules.forEach((module: any) => {
    if (module.units && Array.isArray(module.units)) {
      units.push(...module.units.map((unit: any) => ({
        ...unit,
        moduleTitle: module.title,  // optional: attach module info to unit
        moduleOrder: module.order
      })));
    }
  });

  return units;
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
