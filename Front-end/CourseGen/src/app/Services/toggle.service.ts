import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ToggleService {
  private collapsed = new BehaviorSubject<boolean>(true);
  isCollapsed$ = this.collapsed.asObservable();

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
}
