import { Component } from '@angular/core';
import { Router, NavigationEnd } from "@angular/router";
import { filter } from 'rxjs/operators';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'CourseGen';
  Exclusion = false;

  constructor(private router: Router) {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      const currentUrl = this.router.url;
      this.Exclusion = 
        currentUrl === '/admin-login' ||
        currentUrl === '/register' ||
        currentUrl === '/login' ||
        currentUrl === '/';
    });
  }
}
