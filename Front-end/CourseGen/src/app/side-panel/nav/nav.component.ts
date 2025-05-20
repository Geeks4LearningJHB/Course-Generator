import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { faHome } from '@fortawesome/free-solid-svg-icons';
import { AuthService } from '../../Services/auth.service';
import { ToggleService } from '../../Services/toggle.service';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css'],
})
export class NavComponent implements OnInit {
  faHome = faHome;
  userRole: string | null = null;

  constructor(
    public authService: AuthService,
    public toggleService: ToggleService, // Changed to public
    private router: Router,
    private activatedRoute: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.authService.userRole$.subscribe((role) => {
      this.userRole = role;
    });
  }

  logout(): void {
    this.authService.logout();
  }
}