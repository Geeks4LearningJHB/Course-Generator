import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, BehaviorSubject, Observable, of, tap } from 'rxjs';
import { PendingDTO } from '../Admin/dtos/pending-dto.model';
import { TrainerDTO } from '../Admin/dtos/TrainerDTO';

@Injectable({
  providedIn: 'root'
})
export class UserManagementService {
  private apiUrl = 'http://localhost:8080/Admin';

  private pendingTrainersSubject = new BehaviorSubject<PendingDTO[]>([]);
  pendingTrainers$ = this.pendingTrainersSubject.asObservable();
  
  constructor(private http: HttpClient) {}

   // Fetch trainers and update BehaviorSubject
   fetchPendingTrainers(): Observable<PendingDTO[]> {
    return this.http.get<PendingDTO[]>(`${this.apiUrl}/pending-trainers`).pipe(
      tap((trainers) => this.pendingTrainersSubject.next(trainers))
    );
  }

  // Fetch pending trainers
  getPendingTrainers(): Observable<PendingDTO[]> {
    return this.http.get<PendingDTO[]>(`${this.apiUrl}/pending-trainers`);
  }



  approveTrainer(userId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/approve-trainer/${userId}`, {}).pipe(
      tap(() => this.fetchPendingTrainers().subscribe()) // Refresh trainers after approval
    );
  }

  rejectTrainer(userId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/reject-trainer/${userId}`, {}).pipe(
      tap(() => this.fetchPendingTrainers().subscribe()) // Refresh trainers after rejection
    );
  }

  updateTrainerStatus(email: string, status: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/update-status`, { email, status });
}

  
  

  getAllTrainers(): Observable<TrainerDTO[]> {
    return this.http.get<TrainerDTO[]>(`${this.apiUrl}/AllTrainers`);
  }

  
}
