import { Component, HostListener ,OnInit } from '@angular/core';
import { UserManagementService } from '../../../Services/user-management.service';
import { PendingDTO } from '../../dtos/pending-dto.model';


@Component({
  selector: 'app-user-management',
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.css'
})
export class UserManagementComponent implements OnInit {

  isCollapsed = true;
  pendingTrainers: PendingDTO[] = [];

  constructor(private userManagementService: UserManagementService) {}

  ngOnInit(): void {
    this.loadPendingTrainers();
  }

  loadPendingTrainers(): void {
    this.userManagementService.getPendingTrainers().subscribe((trainers) => {
      this.pendingTrainers = trainers;
    });
  }

  approveTrainer(userId: number): void {
    console.log("Approving trainer with ID:", userId);
    this.userManagementService.approveTrainer(userId).subscribe({
      next: () => {
        console.log("Trainer approved successfully");
        this.loadPendingTrainers(); // Refresh list after approval
      },
      error: (error) => {
        console.error("Error approving trainer:", error);
      }
    });
  }
  
  rejectTrainer(userId: number): void {
    console.log("Rejecting trainer with ID:", userId);
    this.userManagementService.rejectTrainer(userId).subscribe({
      next: () => {
        console.log("Trainer rejected successfully");
        this.loadPendingTrainers(); // Refresh list after rejection
      },
      error: (error) => {
        console.error("Error rejecting trainer:", error);
      }
    });
  }
  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;

    if (!target.closest('.sidebar') && !target.closest('.toggle-btn')) {
      this.isCollapsed = true;
    }
  }
  
}
