import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { LoginService } from '../../Services/adminLogin.service';

@Component({
  selector: 'app-admin-login',
  templateUrl: './admin-login.component.html',
  styleUrls: ['./admin-login.component.css']
})
export class AdminLoginComponent {
  email: string = '';
  password: string = '';
  loginError: string = '';
  LoggingIn: boolean = false;
    successMessage: string = '';

  constructor(private router: Router, private loginService: LoginService) {}

  onLogin() {
    // Reset the error message
    this.loginError = '';

    // Check if email and password are empty
    if (!this.email || !this.password) {
      this.loginError = 'Please enter both email and password.';
      return;
    }

    // If fields are not empty, proceed with login
    this.loginService.loginAdmin({ email: this.email, password: this.password }).subscribe(
      (response) => {
        console.log('Login Response:', response);

        if (response.response === "Success") {
          // Show loading overlay with success message
          this.LoggingIn = true;
          this.successMessage = 'Sign in successfully';
        
        setTimeout(() => {
          this.LoggingIn = false;
          this.router.navigate(['/admin-dashboard']);
        }, 1000); 
      } else {
        this.loginError = 'Invalid credentials!';
      }

      },
      (error) => {
        console.error('Login Error:', error);
        this.loginError = 'Login failed. Please correct your inputs.';
      }
    );
  }
}