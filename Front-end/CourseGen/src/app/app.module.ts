import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './Trainer/login/login.component';
import { RegisterComponent } from './Trainer/register/register.component';
import { DashboardComponent } from './Trainer/dashboard/dashboard.component';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { HttpClientModule } from '@angular/common/http';
import { GenerateContentComponent } from './Trainer/generate-content/generate-content.component';
import { ViewContentComponent } from './Trainer/view-content/view-content.component';
import { ViewCoursesComponent } from './Trainer/view-courses/view-courses.component';
import { AdminDashboardComponent } from './Admin/admin-dashboard/admin-dashboard.component';
// import { UserManagementService } from './Services/user-management.service';
import { UserManagementService } from './Services/user-management.service';
import { AdminLoginComponent } from './Admin/admin-login/admin-login.component';
//import { UserManagementComponent } from './Admin/admin-dashboard/user-management/user-management.component';
@NgModule({
  declarations: [
    
    AppComponent,
    RegisterComponent,
    LoginComponent,
    DashboardComponent,
    LandingPageComponent,
    AdminLoginComponent,
    GenerateContentComponent,
    ViewContentComponent,
    ViewCoursesComponent,
    AdminDashboardComponent,
    

  ],
  imports: [
    HttpClientModule,
    BrowserModule,
    AppRoutingModule,
    FormsModule  
  ],
  providers: [
    provideClientHydration()
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
