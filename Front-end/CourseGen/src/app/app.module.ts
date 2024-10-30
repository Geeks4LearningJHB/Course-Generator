import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';  // Import this module
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { AdminLoginComponent } from './admin-login/admin-login.component';
import { GenerateContentComponent } from './generate-content/generate-content.component';
import { ViewContentComponent } from './view-content/view-content.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    RegisterComponent,
    DashboardComponent,
    LandingPageComponent,
    AdminLoginComponent,
    GenerateContentComponent,
    ViewContentComponent
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
