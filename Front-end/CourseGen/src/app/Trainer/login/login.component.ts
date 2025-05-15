import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { TrainerLoginService } from '../../Services/trainer-login.service';
import { AuthService } from '../../Services/auth.service'; // Import AuthService to set the role

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  errorMessage: string = '';

  constructor(private router: Router, private loginService: TrainerLoginService, private authService: AuthService) {}

  onLogin() {
    this.errorMessage = ''; // Reset the error message

    // Perform the login using the TrainerLoginService
    this.loginService.login(this.email, this.password).subscribe(
      (response) => {
        console.log('Login successful:', response);

        // Set the user role to Trainer after successful login
        this.authService.setUserRole('Trainer');

        // Navigate to the dashboard
        this.router.navigate(['/dashboard']);
      },
      (error) => {
        console.error('Login failed:', error);
        this.errorMessage = 'Invalid email or password. Please try again.'; // Set the error message
      }
    );
  }
}
