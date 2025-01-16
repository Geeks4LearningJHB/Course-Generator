import { HttpClient,HttpErrorResponse, HttpParams  } from '@angular/common/http';
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

  generateCourse(data: { courseTitle: string; difficulty: string; duration: number }): Observable<any> {
    const { difficulty, duration } = data;
    return this.http.post(`${this.apiUrl}generateCourse`, data);
  }
 

  saveGeneratedCourse(generatedCourseData: any): Observable<any> {
    // Extract courseId from generatedCourseData
    const courseId = generatedCourseData.courseId || generatedCourseData.id;
    
    // Create HttpParams with courseId
    const params = new HttpParams().set('courseId', courseId);

    // Make the POST request with params
    return this.http.post(`http://localhost:8080/AI/saveGeneratedCourse`, null, { 
      params: params,
      responseType: 'text'
    }).pipe(
      catchError(this.handleError)
    );
  }

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
  // saveGeneratedCourse(courseData: any): Observable<any> {
  //   return this.http.post('http://localhost:8080/AI/saveGeneratedCourse', courseData);
  // }
  
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

  regenerateUnit(unitId: string) {
    return this.http.post<any>('http://localhost:8080/AI/regenerateText', { unitId });
  }
}
