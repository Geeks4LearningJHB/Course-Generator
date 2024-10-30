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
    console.log('Entered Email:', this.email);
    console.log('Entered Password:', this.password);

    // Trim inputs to avoid whitespace issues
    const trimmedEmail = this.email.trim();
    const trimmedPassword = this.password.trim();

    // Check if credentials match
    if (trimmedEmail === 'Sinenhlanhla_iveco@geeks4learning' && trimmedPassword === 'Password@123') {
      console.log('Login successful!');
      this.router.navigate(['/dashboard']);  // Navigate to dashboard
    } else {
      console.error('Invalid credentials!');
      alert('Invalid credentials!');
    }
  }
}
