import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
// import { PasswordService } from '../../services/password.service';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css']
})
export class ForgotPasswordComponent {
  forgotPasswordForm: FormGroup;
  showNewPassword = false;
  showConfirmPassword = false;
  isLoading = false;
  successMessage = '';
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    // private passwordService: PasswordService,
    private router: Router
  ) {
    this.forgotPasswordForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      newPassword: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required]
    }, { validator: this.passwordMatchValidator });
  }

  passwordMatchValidator(formGroup: FormGroup) {
    const password = formGroup.get('newPassword')?.value;
    const confirmPassword = formGroup.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { mismatch: true };
  }

  onForgetPassword() {
    if (this.forgotPasswordForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const { email, newPassword } = this.forgotPasswordForm.value;

    // this.passwordService.resetPassword(email, newPassword).subscribe({
    //   next: () => {
    //     this.isLoading = false;
    //     this.successMessage = 'Password reset successfully! Redirecting to login...';
    //     setTimeout(() => {
    //       this.router.navigate(['/login']);
    //     }, 3000);
    //   },
    //   error: (err) => {
    //     this.isLoading = false;
    //     this.errorMessage = err.error?.message || 'Password reset failed. Please try again.';
    //     console.error('Password reset error:', err);
    //   }
    // });
  }
}