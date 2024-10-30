import { Component } from '@angular/core';

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
}
