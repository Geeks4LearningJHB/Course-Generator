import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { LoginService } from '../../Services/adminLogin.service';
import { Router } from 'express';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css']  // Changed to `styleUrls`
})
export class ForgotPasswordComponent {
  forgotPasswordForm: FormGroup;

  constructor(private fb: FormBuilder, private loginService: LoginService, private router: Router) {
    this.forgotPasswordForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      confirmPassword: ['', Validators.required]
    });
  }

  onForgetPassword() {
    // if (this.forgotPasswordForm.invalid) {
    //   alert("Please fill in all required fields with valid information.");
    //   return; 
    // }

    const { email, password, confirmPassword } = this.forgotPasswordForm.value;

    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    this.loginService.resetPassword(email, password).subscribe({
      next: () => alert('Password reset successful! Please log in with your new password.'),
      error: (error) => alert('Error resetting password: ' + (error.error.message || 'Please try again later.'))
    });

    
  }
}
