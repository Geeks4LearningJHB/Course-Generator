import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { TrainerLoginService } from '../../Services/trainer-login.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  errorMessage: string = '';

  constructor(private router: Router, private loginService: TrainerLoginService) {}

  onLogin() {
    this.errorMessage = ''; // Reset the error message
    this.loginService.login(this.email, this.password).subscribe(
      (response) => {
        console.log('Login successful:', response);
        this.router.navigate(['/dashboard']);
      },
      (error) => {
        console.error('Login failed:', error);
        this.errorMessage = 'Invalid email or password. Please try again.'; // Set the error message
      }
    );
  }
  
}
