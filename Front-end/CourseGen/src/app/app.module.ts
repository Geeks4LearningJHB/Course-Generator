import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './landing-page/login/login.component';
import { RegisterComponent } from './landing-page/register/register.component';
import { DashboardComponent } from './Trainer/dashboard/dashboard.component';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { HttpClientModule } from '@angular/common/http';
import { GenerateContentComponent } from './Trainer/generate-content/generate-content.component';
import { ViewContentComponent } from './Trainer/view-content/view-content.component';
import { ViewCoursesComponent } from './Trainer/view-courses/view-courses.component';
import { AdminDashboardComponent } from './Admin/admin-dashboard/admin-dashboard.component';
import { UserReviewComponent } from './Admin/admin-dashboard/user-review/user-review.component';
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
    UserReviewComponent
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
