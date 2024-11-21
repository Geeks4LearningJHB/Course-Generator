import { Component, HostListener } from '@angular/core';

@Component({
  selector: 'app-view-content',
  templateUrl: './view-content.component.html',
  styleUrl: './view-content.component.css'
})
export class ViewContentComponent {
  showModifyFields: boolean = false;
  module: string = '';
  topic: string = '';
  details: string = '';
  isCollapsed = true;

  onModifyContent() {
    console.log('Module:', this.module);
    console.log('Topic:', this.topic);
    console.log('Details:', this.details);
    alert('Content modified successfully!');
    // Reset the fields after submission
    this.module = '';
    this.topic = '';
    this.details = '';
  }

  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;

    if (!target.closest('.sidebar') && !target.closest('.toggle-btn')) {
      this.isCollapsed = true;
    }
  }
}
