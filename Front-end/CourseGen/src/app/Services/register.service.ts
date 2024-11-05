import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface TrainerDTO {
  name: string;
  surname: string;
  email: string;
  password: string;
}

@Injectable({
  providedIn: 'root'
})
export class RegisterService {
  private apiUrl = 'http://localhost:8080/Admin/createTrainer'; 

  constructor(private http: HttpClient) {}

  registerUser(trainer: TrainerDTO): Observable<any> {
    return this.http.post<any>(this.apiUrl, trainer);
  }
}
