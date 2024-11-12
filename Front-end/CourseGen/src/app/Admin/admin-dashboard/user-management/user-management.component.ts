import { Component, OnInit } from '@angular/core';
import { UserManagementService } from '../../../Services/user-management.service';
import { PendingDTO } from '../../dtos/pending-dto.model';


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

  loadPendingTrainers(): void {
    // this.userManagementService.getPendingTrainers().subscribe((trainers) => {
    //   this.pendingTrainers = trainers;
    // });
  }

  approveTrainer(userId: number): void {
    this.userManagementService.approveTrainer(userId).subscribe({
      next: () => {
        alert("Trainer approved successfully");
        this.loadPendingTrainers(); // Refresh list after approval
      },
      error: (error) => {
        // Log the error for debugging purposes
        console.error("Error approving trainer:", error);
  
        // Show a detailed alert with the error message (if available)
        const errorMessage = error?.message || "An unknown error occurred while approving the trainer.";
        alert(`Error approving trainer: ${errorMessage}`);
      }
    });
  }
  
  rejectTrainer(userId: number): void {
    this.userManagementService.rejectTrainer(userId).subscribe({
      next: () => {
        alert("Trainer rejected successfully");
        this.loadPendingTrainers(); // Refresh list after rejection
      },
      error: (error) => {
        // Log the error for debugging purposes
        console.error("Error rejecting trainer:", error);
  
        // Show a detailed alert with the error message (if available)
        const errorMessage = error?.message || "An unknown error occurred while rejecting the trainer.";
        alert(`Error rejecting trainer: ${errorMessage}`);
      }
    });
  }
  
  }
  

