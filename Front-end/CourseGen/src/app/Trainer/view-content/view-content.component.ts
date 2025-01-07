import { Component, HostListener, OnInit } from '@angular/core';
import { Unit, ViewContentService } from '../../Services/view-content.service';
import { Course, ViewCoursesService } from '../../Services/view-courses.service';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-view-content',
  templateUrl: './view-content.component.html',
  styleUrls: ['./view-content.component.css']
})
export class ViewContentComponent implements OnInit {
  showModifyFields: boolean = false;
  module: string = '';
  topic: string = '';
  details: string = '';
  isCollapsed = true;
  units: Unit[] = [];
  courses: Course[] = [];
  selectedCourse: Course | null = null;
  generatedData: any;

  // Variables for highlighted text and floating button
  highlightedText: string = '';
  showFloatingButton: boolean = false;
  highlightedTextRange: any = null;
  buttonPosition: { top: string; left: string } = { top: '0px', left: '0px' }; // Define button position
  isModalVisible: boolean = false;
  selectedText: string = '';
  regeneratedText: string = '';

  constructor(
    private router: Router,
    private viewContentService: ViewContentService,
    private viewCoursesService: ViewCoursesService,
    private http: HttpClient
  ) {
    const nav = this.router.getCurrentNavigation();
    this.generatedData = nav?.extras.state?.['data'];
  }

  ngOnInit(): void {
    this.viewContentService.getAllUnits().subscribe({
      next: (data) => {
        this.units = data.map((unit) => ({ ...unit, isExpanded: false }));
      },
      error: (err) => console.error('Error fetching units', err),
    });

    this.viewCoursesService.getCourses().subscribe({
      next: (data) => {
        this.courses = data;
        if (this.courses.length > 0) {
          this.selectedCourse = null;
        }
      },
      error: (err) => console.error('Error fetching courses', err),
    });
  }
  currentUnit: Unit | null = null;

  @HostListener('window:mouseup', ['$event'])
onMouseUp(event: MouseEvent) {
  const selection = window.getSelection();
  if (selection && selection.toString().trim().length > 0) {
    const unitElement = this.findParentUnitElement(selection.getRangeAt(0).commonAncestorContainer);

    if (unitElement) {
      const unitId = unitElement.getAttribute('data-unit-id');
      this.currentUnit = this.units.find(u => u.unitId === unitId) || null;

      if (this.currentUnit) {
        this.highlightedText = selection.toString();
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        this.buttonPosition = {
          top: `${rect.bottom + window.scrollY + 5}px`,
          left: `${rect.left + window.scrollX}px`
        };

        this.showFloatingButton = true;
        return;
      }
    }
  }

  this.showFloatingButton = false;
  this.currentUnit = null;
}

  // Helper function to find the parent unit element
  private findParentUnitElement(element: Node): HTMLElement | null {
    let current: Node | null = element;
  
    // Traverse up the DOM tree to find an element with the attribute 'data-unit-id'
    while (current && !(current instanceof HTMLElement && current.hasAttribute('data-unit-id'))) {
      current = current.parentNode;
    }
  
    // Ensure current is an HTMLElement before returning
    return current instanceof HTMLElement ? current : null;
  }
  

  regenerateSelection() {
    if (!this.highlightedText || !this.currentUnit || !this.selectedCourse) {
      alert('Please select text within a unit to regenerate.');
      return;
    }

    const requestPayload = {
      highlightedText: this.highlightedText,
      moduleId: this.selectedCourse.moduleId,
      unitId: this.currentUnit.unitId,
      startIndex: this.currentUnit.content.indexOf(this.highlightedText),
      endIndex: this.currentUnit.content.indexOf(this.highlightedText) + this.highlightedText.length
    };

    this.viewContentService.regenerateText(requestPayload).subscribe({
      next: (response: any) => {
        this.regeneratedText = response.regeneratedText;
        this.isModalVisible = true;
      },
      error: (error) => {
        console.error('Error regenerating text:', error);
        alert('Failed to regenerate content.');
      }
    });
  }

  confirmUpdate() {
    if (!this.currentUnit) return;

    const request = {
      unitId: this.currentUnit.unitId,
      regeneratedText: this.regeneratedText,
      startIndex: this.currentUnit.content.indexOf(this.selectedText),
      endIndex: this.currentUnit.content.indexOf(this.selectedText) + this.selectedText.length
    };

    this.viewContentService.confirmUpdate(request).subscribe({
      next: () => {
        this.isModalVisible = false;
        // Reload the units to show the updated content
        if (this.selectedCourse) {
          this.onCourseSelect(this.selectedCourse);
        }
      },
      error: (error) => {
        console.error('Error updating unit:', error);
        alert('Failed to update content.');
      }
    });
  }

  toggleUnit(unit: any): void {
    unit.isExpanded = !unit.isExpanded; // Toggle expanded state
  }

  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
  }

  onCourseSelect(course: Course): void {
    this.selectedCourse = course;
    this.viewContentService.getUnitsByModules(this.selectedCourse.moduleId).subscribe({
      next: (data) => {
        this.units = data.map((unit) => ({ ...unit, isExpanded: false }));
      },
      error: (err) => console.error('Error fetching units for selected course:', err),
    });
  }
}
