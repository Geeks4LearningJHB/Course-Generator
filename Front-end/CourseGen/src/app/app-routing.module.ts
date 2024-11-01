import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './landing-page/login/login.component';
import { RegisterComponent } from './landing-page/register/register.component';
import { DashboardComponent } from './Trainer/dashboard/dashboard.component';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { GenerateContentComponent } from './Trainer/generate-content/generate-content.component';
import { ViewContentComponent } from './Trainer/view-content/view-content.component';
// import { ViewCoursesComponent } from './Trainer/view-courses/view-courses.component';
import { ViewCoursesComponent } from './Trainer/dashboard/view-courses/view-courses.component';
import { AdminLoginComponent } from './Admin/admin-login/admin-login.component';
import { AdminDashboardComponent } from './Admin/admin-dashboard/admin-dashboard.component';
import { UserReviewComponent } from './Admin/admin-dashboard/user-review/user-review.component';

const routes: Routes = [
  { path: '', component: LandingPageComponent },  // Default landing page
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'generate-content', component: GenerateContentComponent }, 
  { path: 'view-courses', component: ViewCoursesComponent }, 
  { path: 'view-content', component: ViewContentComponent }, 
  { path: 'admin-login', component: AdminLoginComponent },
  { path: 'admin-dashboard', component: AdminDashboardComponent },
  { path: 'user-review', component: UserReviewComponent },
  { path: '**', redirectTo: '' }  // Redirect unknown routes to the landing page
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
