import { Component, HostListener } from '@angular/core';
import { faHome } from '@fortawesome/free-solid-svg-icons';
// import { AuthService } from '../Services/auth.service';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrl: './nav.component.css'
})
export class NavComponent {
  faHome = faHome;
  isCollapsed = true;
  userRole: string= 'admin';

  // constructor(public authService: AuthService) {}

  // isAuthorized(...roles: string[]): boolean {
  //   return roles.includes(this.authService.getRole());
  // }

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
