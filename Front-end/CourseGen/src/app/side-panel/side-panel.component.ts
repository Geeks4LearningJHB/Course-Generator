import { Component, HostListener, OnInit } from '@angular/core';
import { ActivatedRoute, Router, NavigationEnd, NavigationStart } from '@angular/router';
import { filter } from 'rxjs';
import { faHome } from '@fortawesome/free-solid-svg-icons';
import { AuthService } from '../Services/auth.service';
import { ToggleService } from '../Services/toggle.service';

@Component({
  selector: 'app-side-panel',
  templateUrl: './side-panel.component.html',
  styleUrls: ['./side-panel.component.css']
})
export class SidePanelComponent implements OnInit {
  faHome = faHome;
  userRole: string | null = null;
  headerTitle = 'COURSE GENERATOR';
  showBackButton = true;
  private previousUrl: string | null = null;
  private currentUrl: string | null = null;

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

    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe(() => {
        const currentRoute = this.getChildRoute(this.activatedRoute);
        this.headerTitle = currentRoute.snapshot.data['title'] || this.headerTitle;
        this.showBackButton = currentRoute.snapshot.data['showBackButton'] ?? true;
      });

    this.router.events
      .pipe(filter((event) => event instanceof NavigationStart))
      .subscribe((event: NavigationStart) => {
        this.previousUrl = this.currentUrl;
        this.currentUrl = event.url;
      });
  }

  goBack(): void {
    const currentRoute = this.router.routerState.snapshot.root;
    const previous = currentRoute.firstChild?.data['previous'] || '/dashboard';
    this.router.navigate([previous]);
  }

  private getChildRoute(route: ActivatedRoute): ActivatedRoute {
    while (route.firstChild) {
      route = route.firstChild;
    }
    return route;
  }

  logout(): void {
    this.authService.logout();
  }

  @HostListener('document:click', ['$event'])
onDocumentClick(event: MouseEvent): void {
  const target = event.target as HTMLElement;
  const clickedInside = target.closest('.sidebar') || 
                       target.closest('.nav-btn') || 
                       target.closest('.log-btn');
  
  if (!clickedInside) {
    this.toggleService.collapsePanel();
  }
  }
}