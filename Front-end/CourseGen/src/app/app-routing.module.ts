import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './Trainer/landing-page/login/login.component';
import { RegisterComponent } from './Trainer/landing-page/register/register.component';
import { DashboardComponent } from './Trainer/dashboard/dashboard.component';
import { LandingPageComponent } from './Trainer/landing-page/landing-page.component';
import { ViewCoursesComponent } from './Trainer/dashboard/view-courses/view-courses.component';

const routes: Routes = [
  { path: '', component: LandingPageComponent },  // Default landing page
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'view-course', component: ViewCoursesComponent },
  { path: '**', redirectTo: '' }  // Redirect unknown routes to the landing page
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
