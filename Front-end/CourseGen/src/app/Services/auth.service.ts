import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private userRoleSubject = new BehaviorSubject<string | null>(this.getUserRole());
  userRole$ = this.userRoleSubject.asObservable();

  constructor(@Inject(PLATFORM_ID) private platformId: Object, private http: HttpClient, private router: Router) {

    if (isPlatformBrowser(this.platformId)) {
      const savedRole = sessionStorage.getItem('userRole');
      if (savedRole) {
        this.userRoleSubject.next(savedRole);
      }
    }
  }

  setUserRole(role: string): void {
    if (isPlatformBrowser(this.platformId)) {
      sessionStorage.setItem('userRole', role); // Persist role
  }
  this.userRoleSubject.next(role);
}

  // Get the user role
  getUserRole(): string | null {
    if (isPlatformBrowser(this.platformId)) {
    return sessionStorage.getItem('userRole');
  }
  return null 
}

  // Clear the user role (e.g., on logout)
  clearUserRole(): void {
    if (isPlatformBrowser(this.platformId)) {
      sessionStorage.removeItem('userRole');
  }
  this.userRoleSubject.next(null);
}

  // Logout and redirect to login page
  logout(): void {
    this.clearUserRole();
    this.router.navigate(['/']);
  }
}