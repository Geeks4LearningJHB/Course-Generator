import { Component, HostListener, OnInit } from '@angular/core';
import { faHome } from '@fortawesome/free-solid-svg-icons';
import { AuthService } from '../Services/auth.service';
// import { UserService } from '../Services/user.service';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css'],
})
export class NavComponent implements OnInit {
  faHome = faHome;
  isCollapsed = true;
  userRole: string | null = null;

  constructor(private authService: AuthService) { }

  ngOnInit(): void {
    // Listen for role changes
    this.authService.userRole$.subscribe((role) => {
      this.userRole = role;
    });
  }

  logout(): void {
    this.authService.logout();
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
