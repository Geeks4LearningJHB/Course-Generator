import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ToggleService {
  private collapsed = new BehaviorSubject<boolean>(true);
  isCollapsed$ = this.collapsed.asObservable();

  private _isCollapsed = new BehaviorSubject<boolean>(false);
  isCollapsed = this._isCollapsed.asObservable();

  private activePanel = new BehaviorSubject<'nav' | 'log'>('nav');
  activePanel$ = this.activePanel.asObservable();

  toggleCollapse(): void {
    this.collapsed.next(!this.collapsed.value);
  }

  showNav(): void {
    this.activePanel.next('nav');
  }

  showLog(): void {
    this.activePanel.next('log');
  }

  toggleNav(): void {
    this._isCollapsed.next(!this._isCollapsed.value);
    console.log('Navigation toggled:', !this._isCollapsed.value);
  }
  
  toggleLog(): void {
    console.log('Log toggled');
    // Implement your logging toggle logic here
  }
}
