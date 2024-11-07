import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-landing-page',
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.css'
})
export class LandingPageComponent {

  constructor(private router: Router ) {}

  navigateWithAnimation(route: string) {
    const landingPage = document.getElementById('landingPage');

    landingPage?.classList.add('zoom-out');

    // setTimeout(() => {
    //   if (role === 'admin') {
    //     this.router.navigate(['/admin']);
    //   } else if (role === 'trainer') {
    //     this.router.navigate(['/trainer']);
    //   }
    // }, 800);  // Match this duration to the animation timing
    setTimeout(() => {
      this.router.navigate([route]);
    }, 800);
  }
}
