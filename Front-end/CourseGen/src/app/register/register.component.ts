import { Component } from '@angular/core';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  constructor() {}

  onRegister() {
    // Add registration logic here
    console.log('Registration form submitted');
  }
}
