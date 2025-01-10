import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ToggleService {
  private collapsed = new BehaviorSubject<boolean>(true);
  isCollapsed$ = this.collapsed.asObservable();

  toggleSidebar(): void {
    this.collapsed.next(!this.collapsed.value);
  }
}
