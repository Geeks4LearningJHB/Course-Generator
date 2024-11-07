// trainer.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
// import { PendingDTO } from '../Admin/admin-dashboard/user-management/user-management.component';

@Injectable({
  providedIn: 'root'
})
export class UserManagementService {
  private apiUrl = 'http://localhost:8080/Admin';  // your backend URL

  constructor(private http: HttpClient) {}

  // // Get pending trainers
  // getPendingTrainers(): Observable<PendingDTO[]> {
  //   return this.http.get<PendingDTO[]>(`${this.apiUrl}/pending-trainers`);
  // }

  // Approve a trainer
  approveTrainer(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/approve-trainer/${id}`, {});
  }

  // Reject a trainer
  rejectTrainer(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/reject-trainer/${id}`, {});
  }
}

