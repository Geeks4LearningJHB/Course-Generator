import { Component, OnInit } from '@angular/core';
import { faHome, faUser, faCog, faSignOutAlt } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.css'
})
export class AdminDashboardComponent {

  faHome = faHome;
  isCollapsed = true;

  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }
}
