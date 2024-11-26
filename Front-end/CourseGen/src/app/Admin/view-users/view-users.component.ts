import { Component, HostListener, OnInit } from '@angular/core';
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
  isCollapsed = true;

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
