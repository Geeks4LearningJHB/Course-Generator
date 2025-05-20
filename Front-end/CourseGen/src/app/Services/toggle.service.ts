import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ToggleService {
  private isCollapsedSubject = new BehaviorSubject<boolean>(true);
  isCollapsed$ = this.isCollapsedSubject.asObservable();

  private activePanelSubject = new BehaviorSubject<'nav' | 'log'>('nav');
  activePanel$ = this.activePanelSubject.asObservable();

  togglePanel(panel?: 'nav' | 'log'): void {
    if (panel) {
      // If clicking a different panel, expand and switch
      if (this.activePanelSubject.value !== panel || this.isCollapsedSubject.value) {
        this.activePanelSubject.next(panel);
        this.isCollapsedSubject.next(false);
      } 
      // If clicking the same panel, toggle collapse
      else {
        this.isCollapsedSubject.next(!this.isCollapsedSubject.value);
      }
    } else {
      // External click or manual toggle
      this.isCollapsedSubject.next(!this.isCollapsedSubject.value);
    }
  }

  collapsePanel(): void {
    this.isCollapsedSubject.next(true);
  }
}
