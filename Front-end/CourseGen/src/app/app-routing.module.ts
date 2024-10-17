import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';

const routes: Routes = [
  { path: 'register', component: RegisterComponent },  // Default route
  { path: 'login', component: LoginComponent },
  { path: '', redirectTo: 'register', pathMatch: 'full' },  // Redirect to Register by default
  { path: '**', redirectTo: 'register' }  // Redirect any unknown routes to Register
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
