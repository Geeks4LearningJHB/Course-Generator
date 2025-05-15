import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TrainerLoginService {
  private apiUrl = 'http://localhost:8080/Admin/Trainerlogin';

  constructor(private http: HttpClient) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post(this.apiUrl, { email, password }, { responseType: 'text' });
  }
  
  
}
