import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './Trainer/landing-page/login/login.component';
import { RegisterComponent } from './Trainer/landing-page/register/register.component';
import { DashboardComponent } from './Trainer/dashboard/dashboard.component';
import { LandingPageComponent } from './Trainer/landing-page/landing-page.component';
import { ViewCoursesComponent } from './Trainer/dashboard/view-courses/view-courses.component';
import { AdminLoginComponent } from './Admin/admin-login/admin-login.component';
import { ViewContentComponent } from './Trainer/dashboard/view-courses/view-content/view-content.component';


@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    RegisterComponent,
    DashboardComponent,
    LandingPageComponent,
    ViewCoursesComponent,
    ViewContentComponent,
    AdminLoginComponent,

  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule  // Add FormsModule here
  ],
  providers: [
    provideClientHydration()
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
