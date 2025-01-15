import { Component, HostListener, OnInit } from '@angular/core';
import { UserManagementService } from '../../Services/user-management.service';
import { TrainerDTO } from '../dtos/TrainerDTO';
import { ToggleService } from '../../Services/toggle.service';

@Component({
  selector: 'app-view-users',
  templateUrl: './view-users.component.html',
  styleUrls: ['./view-users.component.css'] // Ensure 'styleUrls' is plural and matches the actual file
})
export class ViewUsersComponent implements OnInit {
  trainers: TrainerDTO[] = []; // This is used in the HTML
  selectedTrainer: TrainerDTO | null = null;
  isCollapsed = true;

  constructor(private userManagementService: UserManagementService, private toggleService: ToggleService) {}

  ngOnInit(): void {
    this.fetchTrainers();
    this.toggleService.isCollapsed$.subscribe(
      (collapsed) => (this.isCollapsed = collapsed)
    );
  }

  // Fetch trainers from the backend and assign to 'trainers'
  fetchTrainers(): void {
    this.userManagementService.getAllTrainers().subscribe(
      (data) => {
        console.log('Fetched trainers:', data); // Debugging log
        this.trainers = data; // Use the same property referenced in the template
      },
      (error) => {
        console.error('Error fetching trainers:', error);
      }
    );
  }

  // Handle viewing trainer details
  viewDetails(trainer: TrainerDTO): void {
    this.selectedTrainer = trainer;
  }

  toggleTrainerStatus(trainer: TrainerDTO): void {
    const newStatus = trainer.status === 'active' ? 'inactive' : 'active';
    
    this.userManagementService.updateTrainerStatus(trainer.email, newStatus).subscribe(
      (response) => {
        console.log(`Trainer status updated to ${newStatus}`, response);
        trainer.status = newStatus; // Update the status in the UI
      },
      (error) => {
        console.error('Error updating trainer status:', error);
      }
    );
  }
  

  // Close details modal
  closeModal(): void {
    this.selectedTrainer = null;
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
