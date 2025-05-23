import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RegisterService } from '../../Services/register.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  name: string = '';
  surname: string = '';
  email: string = '';
  password: string = '';
  confirmPassword: string = '';
  showPassword: boolean = false; // Toggle for password field
  showConfirmPassword: boolean = false; // Toggle for confirm password field
  rememberMe: boolean = false;
  registrationSuccess: boolean = false;
  isLoading: boolean = false;
  errorMessage: string = '';

  constructor(private registerService: RegisterService, private router: Router) {}

  onRegister() {
    this.isLoading = true;
    this.errorMessage = '';

    const trainer = {
      name: this.name,
      surname: this.surname,
      email: this.email,
      password: this.password
    };

    this.registerService.registerUser(trainer).subscribe(
      response => {
        this.isLoading = false;
        this.registrationSuccess = true;
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 3000);
      },
      error => {
        this.isLoading = false;
        this.errorMessage = error.error?.message || 'Registration failed. Please try again.';
        console.error('Error during registration', error);
      }
    );
  }
}