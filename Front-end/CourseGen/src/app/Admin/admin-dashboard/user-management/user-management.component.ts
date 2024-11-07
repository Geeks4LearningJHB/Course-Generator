import { Component, OnInit } from '@angular/core';
import { UserManagementService } from '../../../Services/user-management.service';
// import { PendingDTO } from './pending-dto.model';
// src/app/models/pending-dto.ts
export interface PendingDTO {
  name: string;
  surname: string;
  id: number;
}

@Component({
  selector: 'app-user-management',
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.css'
})
export class UserManagementComponent implements OnInit {
  pendingTrainers: PendingDTO[] = [];
 
  constructor(private userManagementService: UserManagementService) {}
 
  ngOnInit(): void {
    this.loadPendingTrainers();
  }
 
  // Fetch the pending trainers
  loadPendingTrainers(): void {
    this.userManagementService.getPendingTrainers().subscribe((trainers) => {
      this.pendingTrainers = trainers;
    });
  }
 
  // Approve a trainer
  approveTrainer(id: number): void {
    this.userManagementService.approveTrainer(id).subscribe(response => {
      console.log(response);
      this.loadPendingTrainers();  // Refresh list after approval
    });
  }
 
  // Reject a trainer
  rejectTrainer(id: number): void {
    this.userManagementService.rejectTrainer(id).subscribe(response => {
      console.log(response);
      this.loadPendingTrainers();  // Refresh list after rejection
    });
  }
}

// export { PendingDTO };

