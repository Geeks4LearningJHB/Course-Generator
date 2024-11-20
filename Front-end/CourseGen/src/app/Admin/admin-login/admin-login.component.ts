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

  constructor(private router: Router, private loginService: LoginService) {}

  onLogin() {
    this.loginService.loginAdmin({ email: this.email, password: this.password }).subscribe(
      (response) => {
        console.log('Login Response:', response); 
  
        if (response.response === "Success") { 
          this.router.navigate(['/admin-dashboard']);
        } else {
          alert('Invalid credentials!'); 
        }
      },
      (error) => {
        console.error('Login Error:', error); 
        alert('Login failed: ' + error.message);
      }
    );
  }
  
  
}
