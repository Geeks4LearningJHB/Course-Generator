import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './Trainer/login/login.component';
import { RegisterComponent } from './Trainer/register/register.component';
import { DashboardComponent } from './Trainer/dashboard/dashboard.component';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { GenerateContentComponent } from './Trainer/generate-content/generate-content.component';
// import { AdminGenerateContentComponent } from './Admin/admin-dashboard/admin-generate-content/admin-generate-content.component';
import { ViewContentComponent } from './Trainer/view-content/view-content.component';
import { ViewCoursesComponent } from './Trainer/view-courses/view-courses.component';
import { AdminLoginComponent } from './Admin/admin-login/admin-login.component';
// import { AdminDashboardComponent } from './Admin/admin-dashboard/admin-dashboard.component';
import { ForgotPasswordComponent } from './Trainer/forgot-password/forgot-password.component';
import { ProfileManagementComponent } from './profile-management/profile-management.component';
import { UserManagementComponent } from './Admin/admin-dashboard/user-management/user-management.component';
import { ViewUsersComponent } from './Admin/view-users/view-users.component';
// import { AdminViewCoursesComponent } from './Admin/admin-view-courses/admin-view-courses.component';
// import { AdminViewContentComponent } from './Admin/admin-view-content/admin-view-content.component';
import { CourseSaveComponent } from './Trainer/course-save-component/course-save-component.component';
import { ViewGeneratedCourseComponent } from './Trainer/view-generated-course/view-generated-course.component';
// import { AuthGuard } from './Guards/auth.guards';

const routes: Routes = [
  { path: '', component: LandingPageComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent, data: { tittle:'PASSWORD RESET', showBackButton:true, showLogBtn:true, previous: '/dashboard'} },
  { path: 'dashboard', component: DashboardComponent, data: { title: 'COURSE GENERATOR', showLogBtn:true, showBackButton: false } },
  { path: 'generate-content', component: GenerateContentComponent, data: { title: 'GENERATE COURSE', showBackButton: true, showLogBtn:true, previous: '/dashboard' } },
  // { path: 'admin-generate-content', component: AdminGenerateContentComponent },
  { path: 'view-courses', component: ViewCoursesComponent, data: { title: 'VIEW CONTENT', showBackButton: true, showLogBtn:true, previous: '/dashboard' } },
  // { path: 'admin-view-courses', component: AdminViewCoursesComponent },
  { path: 'view-content', component: ViewContentComponent, data: { title: 'VIEW COURSES', showBackButton: true, showLogBtn:true, previous: '/view-courses' } },
  // { path: 'admin-view-content', component: AdminViewContentComponent },
  { path: 'admin-login', component: AdminLoginComponent },
  { path: 'profile-management', component: ProfileManagementComponent, data: { title: 'PROFILE MANAGEMENT', showBackButton: true, showLogBtn:false, previous: '/dashboard' } },
  // { path: 'admin-dashboard', component: AdminDashboardComponent },
  { path: 'view-users', component: ViewUsersComponent, data: { title: 'VIEW ALL USERS', showBackButton: true, showLogBtn:false, previous: '/dashboard' } },
  { path: 'user-management', component: UserManagementComponent, data: { title: 'USER MANAGEMENT', showBackButton: true, showLogBtn:false, previous: '/dashboard' } },
  { path: 'course-save-component', component: CourseSaveComponent },
  { path: 'view-generated-course', component: ViewGeneratedCourseComponent },
  { path: '**', redirectTo: '' }  // Redirect unknown routes to the landing page
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
