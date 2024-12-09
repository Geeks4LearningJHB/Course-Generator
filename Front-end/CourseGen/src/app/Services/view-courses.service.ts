import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Course {
  id: string;
  moduleName: string;
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class ViewCoursesService {
  private apiUrl = 'http://localhost:8080/AI';

  constructor(private http: HttpClient) { }

  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>(this.apiUrl + '/getAllModules');
  }
}
