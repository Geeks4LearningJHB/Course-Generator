import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './landing-page/login/login.component';
import { RegisterComponent } from './landing-page/register/register.component';
import { DashboardComponent } from './Trainer/dashboard/dashboard.component';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { ViewCoursesComponent } from './Trainer/dashboard/view-courses/view-courses.component';
import { ViewContentComponent } from './Trainer/dashboard/view-courses/view-content/view-content.component';
import { GenerateContentComponent } from './Trainer/dashboard/generate-content/generate-content.component';

const routes: Routes = [
  { path: '', component: LandingPageComponent },  // Default landing page
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'view-course', component: ViewCoursesComponent },
  { path: 'view-content', component: ViewContentComponent },
  { path: 'generate-content', component: GenerateContentComponent },
  { path: '**', redirectTo: '' }  // Redirect unknown routes to the landing page
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
