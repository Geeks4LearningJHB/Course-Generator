import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, Observable, of } from 'rxjs';
import { PendingDTO } from '../Admin/dtos/pending-dto.model';
import { TrainerDTO } from '../Admin/dtos/TrainerDTO';

@Injectable({
  providedIn: 'root'
})
export class UserManagementService {
  private apiUrl = 'http://localhost:8080/Admin';

  constructor(private http: HttpClient) {}

  // Fetch pending trainers
  getPendingTrainers(): Observable<PendingDTO[]> {
    return this.http.get<PendingDTO[]>(`${this.apiUrl}/pending-trainers`);
  }

  // Approve trainer by ID
  approveTrainer(userId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/approve-trainer/${userId}`, {});
  }

  // Reject trainer by ID
  rejectTrainer(userId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/reject-trainer/${userId}`, {});
  }


  
  // Fetch accepted trainers
  getAcceptedTrainers(): Observable<PendingDTO[]> {
    return this.http.get<PendingDTO[]>(`${this.apiUrl}/accepted-trainers`);
  }

  // Fetch rejected trainers
  getRejectedTrainers(): Observable<PendingDTO[]> {
    return this.http.get<PendingDTO[]>(`${this.apiUrl}/rejected-trainers`);
  }

  getAllTrainers(): Observable<TrainerDTO[]> {
    return this.http.get<TrainerDTO[]>(`${this.apiUrl}/AllTrainers`);
  }

  
}
