import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms'; 
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './Trainer/login/login.component';
import { RegisterComponent } from './Trainer/register/register.component';
import { DashboardComponent } from './Trainer/dashboard/dashboard.component';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { GenerateContentComponent } from './Trainer/generate-content/generate-content.component';



@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    RegisterComponent,
    DashboardComponent,
    LandingPageComponent,
    GenerateContentComponent 
    
  ],
  imports: [
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
