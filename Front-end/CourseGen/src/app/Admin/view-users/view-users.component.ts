import { Component, OnInit } from '@angular/core';
import { UserManagementService } from '../../Services/user-management.service';
import { TrainerDTO } from '../dtos/TrainerDTO';

@Component({
  selector: 'app-view-users',
  templateUrl: './view-users.component.html',
  styleUrls: ['./view-users.component.css'] // Ensure 'styleUrls' is plural and matches the actual file
})
export class ViewUsersComponent implements OnInit {
  trainers: TrainerDTO[] = []; // This is used in the HTML
  selectedTrainer: TrainerDTO | null = null;

  constructor(private userManagementService: UserManagementService) {}

  ngOnInit(): void {
    this.fetchTrainers();
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

  // Close details modal
  closeModal(): void {
    this.selectedTrainer = null;
  }
}
