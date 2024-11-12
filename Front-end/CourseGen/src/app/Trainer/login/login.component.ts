import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { LoginService } from '../../Services/adminLogin.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email: string = '';
  password: string = '';

  constructor(private router: Router, private loginService: LoginService) {}

  onLogin() {
    this.loginService.login(this.email, this.password).subscribe(
      (response) => {
        console.log('Login successful:', response);
        this.router.navigate(['/dashboard']);
      },
      (error) => {
        console.error('Login failed:', error);
        alert('Invalid credentials!');
      }
    );
  }
}
