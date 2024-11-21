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
    this.userManagementService.getPendingTrainers().subscribe((trainers) => {
      this.pendingTrainers = trainers;
    });
  }

  async approveTrainer(userId: number): Promise<void> {
    this.showLoading('Approving trainer...');
  
    try {
      await this.userManagementService.approveTrainer(userId).toPromise();
      this.showLoading('Trainer approved successfully!', true);
    } catch (error) {
      console.error('Error approving trainer:', error);
      this.isLoading = false; // Ensure loading indicator is hidden
      // Handle error, e.g., display an error message to the user
    }
  }

  async rejectTrainer(userId: number): Promise<void> {
    this.showLoading('Rejecting trainer...');
    try {
      await this.userManagementService.rejectTrainer(userId).toPromise();
      this.showLoading('Trainer rejected successfully!', true);
    } catch (error) {
      console.error('Error rejecting trainer:', error);
    }
  }

  private showLoading(message: string, refreshList: boolean = false): void {
    this.isLoading = true;
    this.loadingMessage = message;

    setTimeout(() => {
      this.isLoading = false;
      if (refreshList) {
        this.loadPendingTrainers(); // Refresh the list after 2 seconds
      }
    }, 1000);
  }

  toggleSidebar(): void {
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
