import { Component, HostListener, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Router, NavigationEnd, NavigationStart } from '@angular/router';
import { filter } from 'rxjs';
import { faHome } from '@fortawesome/free-solid-svg-icons';
import { AuthService } from '../../Services/auth.service';
import { ToggleService } from '../../Services/toggle.service';
import { Location } from '@angular/common';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css'],
})
export class NavComponent implements OnInit {
  faHome = faHome;
  // isCollapsed = true;
  @Input() isCollapsed: boolean = true;
  userRole: string | null = null;
  headerTitle  = 'COURSE GENERATOR';
  showBackButton = true;
  private previousUrl: string | null = null;
  private currentUrl: string | null = null;

  constructor( private authService: AuthService,
               private toggleService: ToggleService,
               private router: Router,
               private activatedRoute: ActivatedRoute,
              //  private location: Location
              ) { 
    this.toggleService.isCollapsed$.subscribe(
      (collapsed) => (this.isCollapsed = collapsed)
    );
   }

  ngOnInit(): void {
    // Listen for role changes
    this.authService.userRole$.subscribe((role) => {
      this.userRole = role;
    });
    // Listen for route changes to update header dynamically
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe(() => {
        const currentRoute = this.getChildRoute(this.activatedRoute);
        this.headerTitle = currentRoute.snapshot.data['title'] || this.headerTitle;
        this.showBackButton = currentRoute.snapshot.data['showBackButton'] ?? true;
      });

      // Track previous and current URLs
    this.router.events
    .pipe(filter((event) => event instanceof NavigationStart))
    .subscribe((event: NavigationStart) => {
      this.previousUrl = this.currentUrl;
      this.currentUrl = event.url;
    });
    }

    

  // Navigate to the previous page or a default route
  goBack(): void {
    const currentRoute = this.router.routerState.snapshot.root;
    const previous = currentRoute.firstChild?.data['previous'] || '/dashboard';
    this.router.navigate([previous]);
  }

  // Helper method to get the deepest child route
  private getChildRoute(route: ActivatedRoute): ActivatedRoute {
    while (route.firstChild) {
      route = route.firstChild;
    }
    return route;
  }

  logout(): void {
    this.authService.logout();
  }

  toggleSidebar(): void {
    this.isCollapsed = !this.isCollapsed;
    this.toggleService.toggleSidebar();
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;

    if (!target.closest('.sidebar') && !target.closest('.toggle-btn')) {
      this.isCollapsed = true;
    }
  }
}
