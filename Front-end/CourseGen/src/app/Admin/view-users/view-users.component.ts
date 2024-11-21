import { Component, OnInit } from '@angular/core';
import { UserManagementService } from '../../Services/user-management.service';
import { PendingDTO } from '../dtos/pending-dto.model';

@Component({
  selector: 'app-view-users',
  templateUrl: './view-users.component.html',
  styleUrl: './view-users.component.css'
})
export class ViewUsersComponent implements OnInit {
  trainers: PendingDTO[] = [];
  selectedTrainer: PendingDTO | null = null;

  constructor(private userManagementService: UserManagementService) {}

  ngOnInit(): void {
    this.loadAllTrainers();
  }

  loadAllTrainers(): void {
    this.userManagementService.getAllTrainers().subscribe((trainers) => {
      this.trainers = trainers;
    });
  }

  viewDetails(trainer: PendingDTO): void {
    this.selectedTrainer = trainer;
  }

  closeModal(): void {
    this.selectedTrainer = null;
  }
}
