import { Component } from '@angular/core';
import { Router } from '@angular/router';


@Component({
  selector: 'app-admin-login',
  templateUrl: './admin-login.component.html',
  styleUrl: './admin-login.component.css'
})
export class AdminLoginComponent {
  email: string = '';
  password: string = '';

  constructor(private router: Router) {}

  onLogin() {
    if (this.email === 'admin@example.com' && this.password === 'Password123') {
      this.router.navigate(['/dashboard']); // Navigate to dashboard after successful login
    } else {
      alert('Invalid credentials!');
    }
  }
}