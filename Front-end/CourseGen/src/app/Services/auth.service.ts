// import { Injectable } from '@angular/core';

// @Injectable({
//   providedIn: 'root',
// })
// export class AuthService {
//   getRole(): string {
//     throw new Error('Method not implemented.');
//   }
//   private userRole: string | null = null; // Store the current user's role (admin/user)

//   constructor() {}

//   // Set the role after login
//   setUserRole(role: string): void {
//     this.userRole = role;
//     localStorage.setItem('userRole', role); // Optional: Persist in local storage
//   }

//   // Get the role of the current user
//   getUserRole(): string | null {
//     if (!this.userRole) {
//       this.userRole = localStorage.getItem('userRole'); // Retrieve from local storage if needed
//     }
//     return this.userRole;
//   }

//   // Logout the user
//   logout(): void {
//     this.userRole = null;
//     localStorage.removeItem('userRole'); // Clear from local storage
//   }
// }
