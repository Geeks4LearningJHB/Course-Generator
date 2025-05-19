import { Component, OnInit } from '@angular/core';
import { LogService } from '../../Services/log.service';
@Component({
  selector: 'app-user-log',
  templateUrl: './user-log.component.html',
  styleUrl: './user-log.component.css'
})
export class UserLogComponent implements OnInit {
logs: any[] = [];

  constructor(private logService: LogService) {}

  ngOnInit(): void {
    this.fetchLogs();
  }

  fetchLogs(): void {
    this.logService.getLogs().subscribe({
      next: (data) => this.logs = data,
      error: (err) => console.error('Error fetching logs:', err)
    });
  }
}
