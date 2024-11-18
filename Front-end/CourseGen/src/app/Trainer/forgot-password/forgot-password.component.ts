import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrl: './forgot-password.component.css'
})
export class ForgotPasswordComponent {
onForgetPassword() {
throw new Error('Method not implemented.');
}
  forgotPasswordForm: FormGroup;

  constructor(private fb: FormBuilder){
    this.forgotPasswordForm = this.fb.group({
      email: ['', Validators.required],
      password: ['', Validators.required],
      newPassword: ['', Validators.required]
    });
  }

}
