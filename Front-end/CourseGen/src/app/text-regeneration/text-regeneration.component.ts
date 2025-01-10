// text-regeneration.component.ts
import { Component, OnInit, ElementRef, ViewChild, HostListener } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-text-regeneration',
  templateUrl: './text-regeneration.component.html',
  styleUrls: ['./text-regeneration.component.css']
})
export class TextRegenerationComponent implements OnInit {
  moduleId: string = '';
  unitId: string = '';
  content: string = '';
  regeneratedText: string = '';
  selectionStart: number = 0;
  selectionEnd: number = 0;
  isModalVisible: boolean = false;
  showFloatingButton: boolean = false;
  buttonPosition = { top: '0px', left: '0px' };
  
  @ViewChild('floatingButton') floatingButton!: ElementRef;
  
  constructor(private http: HttpClient) {}
  
  ngOnInit() {
    this.loadUnitContent();
  }
  
  onTextSelection(event: MouseEvent) {
    const selection = window.getSelection();
    if (selection && selection.toString().length > 0) {
      // Get selection position
      const range = selection.getRangeAt(0);
      const preSelectionRange = range.cloneRange();
      preSelectionRange.selectNodeContents(range.startContainer);
      preSelectionRange.setEnd(range.startContainer, range.startOffset);
      
      this.selectionStart = preSelectionRange.toString().length;
      this.selectionEnd = this.selectionStart + selection.toString().length;
      
      // Position the floating button near the mouse position
      const rect = range.getBoundingClientRect();
      this.buttonPosition = {
        top: `${rect.bottom + window.scrollY + 10}px`,  // 10px below selection
        left: `${rect.left + window.scrollX}px`
      };
      
      this.showFloatingButton = true;
    } else {
      this.showFloatingButton = false;
    }
  }
  
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    // Hide floating button if clicked outside the selection and button
    if (this.floatingButton && !this.floatingButton.nativeElement.contains(event.target)) {
      const selection = window.getSelection();
      if (!selection || selection.toString().length === 0) {
        this.showFloatingButton = false;
      }
    }
  }
  
  regenerateSelection() {
    const selectedText = window.getSelection()?.toString();
    if (!selectedText) return;
    
    const request = {
      moduleId: this.moduleId,
      unitId: this.unitId,
      highlightedText: selectedText,
      startIndex: this.selectionStart,
      endIndex: this.selectionEnd
    };
    
    this.showFloatingButton = false; // Hide floating button while processing
    
    this.http.post<any>('/api/regenerateText', request).subscribe(
      response => {
        this.regeneratedText = response.regeneratedText;
        this.isModalVisible = true;
      },
      error => {
        console.error('Error regenerating text:', error);
        alert('Error regenerating text. Please try again.');
      }
    );
  }

  // Add the missing confirmUpdate method
  confirmUpdate() {
    const request = {
      unitId: this.unitId,
      regeneratedText: this.regeneratedText,
      startIndex: this.selectionStart,
      endIndex: this.selectionEnd
    };
    
    this.http.post<any>('/api/confirmUpdate', request).subscribe(
      response => {
        this.isModalVisible = false;
        this.loadUnitContent(); // Reload the content after update
      },
      error => {
        console.error('Error updating unit:', error);
        alert('Error updating unit. Please try again.');
      }
    );
  }

  // Add the missing loadUnitContent method
  private loadUnitContent() {
    // Replace with your actual API endpoint
    this.http.get<any>(`/api/units/${this.unitId}`).subscribe(
      unit => {
        this.content = unit.content;
      },
      error => {
        console.error('Error loading unit content:', error);
      }
    );
  }
}