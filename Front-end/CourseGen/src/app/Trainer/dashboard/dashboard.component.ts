import { Component, HostListener } from '@angular/core';
import { AuthService } from '../../Services/auth.service';
import { ToggleService } from '../../Services/toggle.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  isCollapsed = true;
  userRole: string | null = null;

  constructor(private authService: AuthService, private toggleService: ToggleService ) { }

  ngOnInit(): void {
    // Listen for role changes
    this.authService.userRole$.subscribe((role) => {
      this.userRole = role;
    });
    this.toggleService.isCollapsed$.subscribe(
      (collapsed) => (this.isCollapsed = collapsed)
    );
  }

  logout(): void {
    this.authService.logout();
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
