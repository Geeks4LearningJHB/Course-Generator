import { Component } from '@angular/core';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  constructor() {}

  onSubmit() {
    // Add login logic here
    console.log('Login form submitted');
  }
}
