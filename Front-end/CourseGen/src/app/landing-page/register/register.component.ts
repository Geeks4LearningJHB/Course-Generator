import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css'], // Fixed the property name to styleUrls
})
export class RegisterComponent {
  name: string = '';
  surname: string = '';
  email: string = '';
  password: string = '';
  confirmPassword: string = '';
  registrationSuccess: boolean = false; // To track registration success

  constructor(private router: Router) {}

  onRegister() {
    // Here you would typically make an HTTP request to your backend to register the user
    console.log('Registration form submitted');
    
    // Simulate registration logic
    this.registrationSuccess = true; // Assume registration was successful

    // Redirect to the sign-in page after a short delay
    setTimeout(() => {
      this.router.navigate(['/login']);
    }, 3000); // Wait for 3 seconds before redirecting
  }
}
