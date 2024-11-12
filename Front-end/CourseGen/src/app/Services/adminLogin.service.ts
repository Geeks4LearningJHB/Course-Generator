// src/app/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class LoginService {
  private apiUrl = 'http://localhost:8080/Admin/Adminlogin';
  private resetPasswordUrl = 'http://localhost:8080/Admin/reset-password';

  constructor(private http: HttpClient) {}

  loginAdmin(credentials: { email: string; password: string }): Observable<any> {
    return this.http.post<any>(this.apiUrl, credentials).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Login error:', error); // Log the error for debugging
        return throwError('Something went wrong; please try again later.');
      })
    );
  }

  resetPassword(email: string, newPassword: string): Observable<any> {
    const params = new HttpParams()
      .set('email', email)
      .set('newPassword', newPassword);

    return this.http.post(this.resetPasswordUrl, {}, { params }).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Reset password error:', error); // Log the error for debugging
        return throwError('Something went wrong; please try again later.');
      })
    );
  }
}
