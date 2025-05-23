import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { TrainerLoginService } from '../../Services/trainer-login.service';
import { AuthService } from '../../Services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  errorMessage: string = '';
  showPassword: boolean = false; // Add this line to declare the property

  constructor(
    private router: Router, 
    private loginService: TrainerLoginService, 
    private authService: AuthService
  ) {}

  onLogin() {
    this.errorMessage = ''; // Reset the error message

    this.loginService.login(this.email, this.password).subscribe(
      (response) => {
        console.log('Login successful:', response);
        this.authService.setUserRole('Trainer');
        this.router.navigate(['/dashboard']);
      },
      (error) => {
        console.error('Login failed:', error);
        this.errorMessage = 'Invalid email or password. Please try again.';
      }
    );
  }

  // Optional: Add a method to toggle password visibility if you prefer
  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }
}