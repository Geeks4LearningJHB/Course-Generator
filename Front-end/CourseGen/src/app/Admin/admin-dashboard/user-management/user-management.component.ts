import { Component, HostListener, OnInit } from '@angular/core';
import { UserManagementService } from '../../../Services/user-management.service';
import { PendingDTO } from '../../dtos/pending-dto.model';

@Component({
  selector: 'app-user-management',
  templateUrl: './user-management.component.html',
  styleUrls: ['./user-management.component.css'],
})
export class UserManagementComponent implements OnInit {
  isCollapsed = true;
  isLoading: boolean = false;
  loadingMessage: string = '';
  pendingTrainers: PendingDTO[] = [];

  constructor(private userManagementService: UserManagementService) {}

  ngOnInit(): void {
    this.loadPendingTrainers();
  }

  loadPendingTrainers(): void {
    this.userManagementService.getPendingTrainers().subscribe({
      next: (trainers) => {
        this.pendingTrainers = trainers; // Update the list in the component
      },
      error: (error) => {
        console.error("Error fetching pending trainers:", error);
        // Optionally, display an error message to the user
      }
    });
  }
  

  approveTrainer(userId: number): void {
    console.log("Approving trainer with ID:", userId);
  
    this.userManagementService.approveTrainer(userId).subscribe({
      next: (response) => {
        console.log("Trainer approved successfully:", response.message); // Handle the JSON response
        this.loadPendingTrainers();
        this.showLoading('Trainer approved successfully!', true);
      },
      error: (error) => {
        console.error("Error approving trainer:", error.error.message); // Handle error message
      }
    });
  }
  
  rejectTrainer(userId: number): void {
    console.log("Rejecting trainer with ID:", userId);
  
    this.userManagementService.rejectTrainer(userId).subscribe({
      next: (response) => {
        console.log("Trainer rejected successfully:", response.message); // Handle the JSON response
        this.loadPendingTrainers(); // Refresh the list
        this.showLoading('Trainer rejected successfully!', true);
      },
      error: (error) => {
        console.error("Error rejecting trainer:", error.error.message); // Handle error message
      }
    });
  }

  private showLoading(message: string, refreshList: boolean = false): void {
    this.isLoading = true;
    this.loadingMessage = message;
 
    setTimeout(() => {
      this.isLoading = false;
      if (refreshList) {
        this.loadPendingTrainers(); // Refresh the list after 2 seconds
      }
    }, 2000);
  }
  
  
  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;

    if (!target.closest('.sidebar') && !target.closest('.toggle-btn')) {
      this.isCollapsed = true;
    }
  }
}
