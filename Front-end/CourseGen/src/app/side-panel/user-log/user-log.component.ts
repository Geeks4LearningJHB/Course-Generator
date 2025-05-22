import { Component, OnInit } from '@angular/core';
import { LogService } from '../../Services/log.service';
import { ToggleService } from '../../Services/toggle.service';
import { HostListener } from '@angular/core';

@Component({
  selector: 'app-user-log',
  templateUrl: './user-log.component.html',
  styleUrl: './user-log.component.css'
})
export class UserLogComponent implements OnInit {

  isOpen = false;
logs: { message: string; action:string; timestamp: string }[] = [];
ngOnInit(): void {
  // Temporary hardcoded logs until API is ready
  this.logs = [
    { message: 'Java OOP', action: 'Generated', timestamp: '2023-10-01T12:00:00Z' },
    { message: 'Node.js Fundamentals', action: 'Updated', timestamp: '2023-10-02T09:30:00Z' },
    { message: 'Artificial Intelligence', action: 'Edited', timestamp: '2023-10-03T15:45:00Z' }
  ];
  // Uncomment below when API is ready
  // this.fetchLogs();
}
// Helper to format timestamp as "2 hours ago", "yesterday", or date string
formatTimestamp(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffDay === 1) return 'yesterday';
  if (diffDay > 1) return date.toLocaleDateString();
  if (diffHr >= 1) return `${diffHr} hour${diffHr > 1 ? 's' : ''} ago`;
  if (diffMin >= 1) return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
  return 'just now';
}


  constructor( private logService: LogService,
               public toggleService: ToggleService
  ) {}

  // ngOnInit(): void {
  //   this.fetchLogs();
  // }

  fetchLogs(): void {
    this.logService.getLogs().subscribe({
      next: (data) => this.logs = data.map((entry: any) => ({
        message: entry.message ?? entry.text ?? '',
        timestamp: entry.timestamp ?? entry.date ?? '',
        action: entry.action ?? entry.text ??''
      })),
      error: (err) => console.error('Error fetching logs:', err)
    });
  }

  openPanel() {
    this.isOpen = true;
  }

  closePanel() {
    this.isOpen = false;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.side-panel')) {
      this.closePanel();
    }
  }
}
