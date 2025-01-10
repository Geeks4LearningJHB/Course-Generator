import { Component, HostListener, OnInit,AfterViewInit } from '@angular/core';
import {Unit, ViewContentService } from '../../Services/view-content.service';
import {
  Course,
  ViewCoursesService,
} from '../../Services/view-courses.service';
import { ActivatedRoute, Router } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { HttpClient } from '@angular/common/http';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas'

export interface ListItem {
  text?: string;
  subItems?: string[];
  language?: string;
  code?: string;
}

export interface ParsedSection {
  heading: string;
  content: string | ListItem[];
}

export interface ParsedUnit {
  // monthNumber: number;
  title: string;
  introduction: string;
  keyConcepts: string[];
  sections: ParsedSection[];
  isLoaded?: boolean;
}

// interface Section {
//   heading: string;
//   content: string | string[] | CodeBlock[] | ListItem[];
// }

// interface CodeBlock {
//   language: string;
//   code: string;
// }

// interface ListItem {
//   text: string;
//   subItems?: string[];
// }

// interface UnitWithState extends Unit {
//   isExpanded?: boolean;
//   isLoaded?: boolean;
// }

// interface UnitContent {
//   title: string;
//   introduction: string;
//   keyConcepts: string[];
//   sections: Section[];
//   isLoaded: boolean;
// }

@Component({
  selector: 'app-view-content',
  templateUrl: './view-content.component.html',
  styleUrls: ['./view-content.component.css'],
})
export class ViewContentComponent implements AfterViewInit  {
  showModifyFields: boolean = false;
  module: string = '';
  topic: string = '';
  details: string = '';
  isCollapsed = true;
  units: Unit[] = [];
  courses: Course[] = [];
  selectedCourse: Course | null = null;
  generatedData: any;
  courseName: string = '';
  currentCourseId: string = '';

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
    private route: ActivatedRoute,
    private viewCoursesService: ViewCoursesService,
    private http: HttpClient
  ) {
    const nav = this.router.getCurrentNavigation();
    this.generatedData = nav?.extras.state?.['data'];
  }
 
  ngAfterViewInit() {
    const unitElement = document.querySelector('#unit-element');
    if (unitElement) {
      unitElement.addEventListener('click', () => {
        console.log('Unit Element clicked!');
      });
    }
  }
  

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      const courseId = params['id'];
      if (courseId) {
        this.currentCourseId = courseId;
        this.loadCourseContent(courseId);
      } else {
        console.error('No course ID found in query parameters.');
      }
    });
  }

  loadCourseContent(courseId: string): void {
    this.viewCoursesService.getModuleById(courseId).subscribe({
      next: (course) => {
        this.courseName = course.moduleName;
      },
      error: (err) => console.error('Error fetching course details:', err),
    });

    this.viewContentService.getUnitsByModules(courseId).subscribe({
      next: (data) => {
        this.units = data.map((unit) => ({ ...unit, isExpanded: false }));
      },
      error: (err) => console.error('Error fetching course content:', err),
    });
  }

  currentUnit: Unit | null = null;

  @HostListener('window:mouseup', ['$event'])
  onMouseUp(event: MouseEvent) {
    const selection = window.getSelection();
    console.log('Selection:', selection?.toString());
  
    if (selection && selection.toString().trim().length > 0) {
      const unitElement = this.findParentUnitElement(
        selection.getRangeAt(0).commonAncestorContainer
      );
      console.log('Unit Element:', unitElement);
  
      if (unitElement) {
        const unitId = unitElement.getAttribute('data-unit-id');
        console.log('Unit ID:', unitId);
  
        this.currentUnit = this.units.find((u) => u.unitId === unitId) || null;
  
        if (this.currentUnit) {
          this.highlightedText = selection.toString();
          const range = selection.getRangeAt(0);
          const rect = range.getBoundingClientRect();
  
          this.buttonPosition = {
            top: `${rect.bottom + window.scrollY + 5}px`,
            left: `${rect.left + window.scrollX}px`,
          };
  
          console.log('Button Position:', this.buttonPosition);
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
    while (
      current &&
      !(current instanceof HTMLElement && current.hasAttribute('data-unit-id'))
    ) {
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
      endIndex:
        this.currentUnit.content.indexOf(this.highlightedText) +
        this.highlightedText.length,
    };

    this.viewContentService.regenerateText(requestPayload).subscribe({
      next: (response: any) => {
        this.regeneratedText = response.regeneratedText;
        this.isModalVisible = true;
      },
      error: (error) => {
        console.error('Error regenerating text:', error);
        alert('Failed to regenerate content.');
      },
    });
  }

  confirmUpdate() {
    if (!this.currentUnit) return;

    const request = {
      unitId: this.currentUnit.unitId,
      regeneratedText: this.regeneratedText,
      startIndex: this.currentUnit.content.indexOf(this.selectedText),
      endIndex:
        this.currentUnit.content.indexOf(this.selectedText) +
        this.selectedText.length,
    };

    this.viewContentService.confirmUpdate(request).subscribe({
      next: () => {
        this.isModalVisible = false;
        // Reload the units to show the updated content
        this.loadCourseContent(this.currentCourseId);
      },
      error: (error) => {
        console.error('Error updating unit:', error);
        alert('Failed to update content.');
      },
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
    this.viewContentService
      .getUnitsByModules(this.selectedCourse.moduleId)
      .subscribe({
        next: (data) => {
          this.units = data.map((unit) => ({ ...unit, isExpanded: false }));
        },
        error: (err) =>
          console.error('Error fetching units for selected course:', err),
      });
  }

  downloadPDF(): void {
    const contentElement = document.querySelector('.course-content') as HTMLElement;

    if (contentElement) {
      html2canvas(contentElement).then((canvas) => {
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const imgWidth = 190; // Adjust for A4 width with margins
        const pageHeight = 295; // A4 page height
        const imgHeight = (canvas.height * imgWidth) / canvas.width;

        let heightLeft = imgHeight;
        let position = 10; // Start position

        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;

        while (heightLeft > 0) {
          position = heightLeft - imgHeight;
          pdf.addPage();
          pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
          heightLeft -= pageHeight;
        }

        pdf.save('CourseContent.pdf');
      });
    } else {
      console.error('Content element not found!');
    }
  }
}
/*
const unitElement = document.querySelector('#unit-element');
console.log('Unit Element:', unitElement);
if (!unitElement) {
  console.warn('Unit Element is null or undefined.');
}



*/