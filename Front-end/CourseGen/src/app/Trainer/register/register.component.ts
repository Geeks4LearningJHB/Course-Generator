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
  registrationSuccess: boolean = false;

  constructor(private registerService: RegisterService, private router: Router) {}

  onRegister() {
    const trainer = {
      name: this.name,
      surname: this.surname,
      email: this.email,
      password: this.password
    };

    this.registerService.registerUser(trainer).subscribe(
      response => {
        console.log('Registration successful', response);
        this.registrationSuccess = true;
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 3000);
      },
      error => {
        console.error('Error during registration', error);
      }
    );
  }
}
