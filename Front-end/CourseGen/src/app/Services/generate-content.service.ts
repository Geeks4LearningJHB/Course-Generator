import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GenerateContentService {

  private apiUrl = 'http://localhost:8080/AI/generateCourse';

  constructor(private http: HttpClient) {}

  generateCourse(courseData: { courseTitle: string, difficulty: string, duration: number }): Observable<any> {
    
    return this.http.post(this.apiUrl, courseData);
  }
}
