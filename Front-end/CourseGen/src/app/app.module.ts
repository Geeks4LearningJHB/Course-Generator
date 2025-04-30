import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';
import { FormsModule,ReactiveFormsModule } from '@angular/forms';  
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { LoginComponent } from './Trainer/login/login.component';
import { RegisterComponent } from './Trainer/register/register.component';
import { DashboardComponent } from './Trainer/dashboard/dashboard.component';
import { AdminDashboardComponent } from './Admin/admin-dashboard/admin-dashboard.component';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { ViewContentComponent } from './Trainer/view-content/view-content.component';
import { AdminViewContentComponent } from './Admin/admin-view-content/admin-view-content.component';
import { GenerateContentComponent } from './Trainer/generate-content/generate-content.component';
import { AdminGenerateContentComponent } from './Admin/admin-dashboard/admin-generate-content/admin-generate-content.component';
import { AdminLoginComponent } from './Admin/admin-login/admin-login.component';
import { ForgotPasswordComponent } from './Trainer/forgot-password/forgot-password.component';
import { ProfileManagementComponent } from './profile-management/profile-management.component';
import { ViewCoursesComponent } from './Trainer/view-courses/view-courses.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { UserManagementComponent } from './Admin/admin-dashboard/user-management/user-management.component';
import { ViewUsersComponent } from './Admin/view-users/view-users.component';

import { AdminViewCoursesComponent } from './Admin/admin-view-courses/admin-view-courses.component';
import { NavComponent } from './side-panel/nav/nav.component';
import { CourseSaveComponent } from './Trainer/course-save-component/course-save-component.component';
import { ViewGeneratedCourseComponent } from './Trainer/view-generated-course/view-generated-course.component';
import { ContentParserService } from './Services/content-parser.service';
// import { TextRegenerationComponent } from './text-regeneration/text-regeneration.component';
// import { TextRegenerationComponent } from './text-regeneration/text-regeneration.component';
import { AuthService } from './Services/auth.service';
import { SidePanelComponent } from './side-panel/side-panel.component';
import { UserLogComponent } from './side-panel/user-log/user-log.component';

@NgModule({
  declarations: [
    
    AppComponent,
    RegisterComponent,
    LoginComponent,
    DashboardComponent,
    LandingPageComponent,
    ViewContentComponent,
    GenerateContentComponent,
    AdminLoginComponent,
    ForgotPasswordComponent,
    ProfileManagementComponent,
    ViewCoursesComponent,
    AdminDashboardComponent,
    UserManagementComponent,
    ViewUsersComponent,
    AdminGenerateContentComponent,
    AdminViewContentComponent,
    AdminViewCoursesComponent,
    CourseSaveComponent,
    ViewGeneratedCourseComponent,
    SidePanelComponent,
    UserLogComponent,
    NavComponent,
   
  ],
  imports: [
    HttpClientModule,
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    FormsModule,
    FontAwesomeModule,
    ReactiveFormsModule
  ],
  providers: [
    provideClientHydration(),
    ContentParserService,
    AuthService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
