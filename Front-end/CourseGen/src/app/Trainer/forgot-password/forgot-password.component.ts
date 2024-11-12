import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { LoginService } from '../../Services/adminLogin.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrl: './forgot-password.component.css'
})
export class ForgotPasswordComponent {

  forgotPasswordForm: FormGroup;

  constructor(private fb: FormBuilder, private loginservice:LoginService, private router: Router){
    this.forgotPasswordForm = this.fb.group({
      email: ['', Validators.required],
      password: ['', Validators.required],
      newPassword: ['', Validators.required]
    });
  }

    onForgetPassword() {
      if (this.forgotPasswordForm.invalid) {
        alert("Please fill in all required fields with valid information.");
        return; 
      }
  
      const { email, password, newPassword } = this.forgotPasswordForm.value;
  
      if (password !== newPassword) {
        alert("Passwords do not match!");
        return;
      }
  
      this.loginservice.resetPassword(email, newPassword).subscribe({
        next: () => {
          alert('Password reset successful! Please log in with your new password.');
          // Navigate to the login or home page, or any other desired component
          this.router.navigate(['/admin-login']); // Replace with your target route
        },
        error: (error) => {
          alert('Error resetting password: ' + (error.error.message || 'Please try again later.'));
        }
      });
    }

}
