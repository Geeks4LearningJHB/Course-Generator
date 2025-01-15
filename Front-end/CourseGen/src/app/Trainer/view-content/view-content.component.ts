import { Component, HostListener, OnInit, AfterViewInit } from '@angular/core';
import { Unit, ViewContentService } from '../../Services/view-content.service';
import { Course, ViewCoursesService } from '../../Services/view-courses.service';
import { ToggleService } from '../../Services/toggle.service';
import { ActivatedRoute, Router } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
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
export class ViewContentComponent implements AfterViewInit {
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
  regenerationReason: string = '';

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
    private http: HttpClient,
    private toggleService: ToggleService
  ) {
    const nav = this.router.getCurrentNavigation();
    this.generatedData = nav?.extras.state?.['data'];
  }

  // ngOnInit(): void {
  //   this.viewContentService.getAllUnits().subscribe({
  //     next: (data) => {
  //       this.units = data.map((unit) => ({ ...unit, isExpanded: false }));
  //     },
  //     error: (err) => console.error('Error fetching units', err),
  //   });

  //   this.viewCoursesService.getCourses().subscribe({
  //     next: (data) => {
  //       this.courses = data;
  //       if (this.courses.length > 0) {
  //         this.selectedCourse = null;
  //       }
  //     },
  //     error: (err) => console.error('Error fetching courses', err),
  //   });
  //   this.toggleService.isCollapsed$.subscribe(
  //     (collapsed) => (this.isCollapsed = collapsed)
  //   );
  // }
  currentUnit: Unit | null = null;

//   @HostListener('window:mouseup', ['$event'])
// onMouseUp(event: MouseEvent) {
//   const selection = window.getSelection();
//   if (selection && selection.toString().trim().length > 0) {
//     const unitElement = this.findParentUnitElement(selection.getRangeAt(0).commonAncestorContainer);

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

  // currentUnit: Unit | null = null;

  @HostListener('window:mouseup', ['$event'])
  onMouseUp(event: MouseEvent) {
    const selection = window.getSelection();
    
    if (selection && selection.toString().trim().length > 0) {
      const unitElement = this.findParentUnitElement(
        selection.getRangeAt(0).commonAncestorContainer
      );
      
      if (unitElement) {
        const unitId = unitElement.getAttribute('data-unit-id');
        
        this.currentUnit = this.units.find((u) => u.unitId === unitId) || null;
        
        if (this.currentUnit) {
          this.highlightedText = selection.toString();
          const range = selection.getRangeAt(0);
          const rect = range.getBoundingClientRect();
          
          this.buttonPosition = {
            top: `${rect.bottom + window.scrollY + 5}px`,
            left: `${rect.left + window.scrollX}px`,
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
    while (
      current &&
      !(current instanceof HTMLElement && current.hasAttribute('data-unit-id'))
    ) {
      current = current.parentNode;
    }
    return current instanceof HTMLElement ? current : null;
  }

  regenerateSelection() {
    if (!this.highlightedText || !this.currentUnit) {
      alert('Please select text within a unit to regenerate.');
      return;
    }

    // Log the current state for debugging
    console.log('Current Unit:', this.currentUnit);
    console.log('Highlighted Text:', this.highlightedText);
    console.log('Current Course ID:', this.currentCourseId);

    const requestPayload = {
      highlightedText: this.highlightedText,
      moduleId: this.currentCourseId,
      unitId: this.currentUnit.unitId,
      startIndex: this.currentUnit.content.indexOf(this.highlightedText),
      endIndex: this.currentUnit.content.indexOf(this.highlightedText) + this.highlightedText.length,
    };

    // Log the request payload
    console.log('Request Payload:', requestPayload);

    this.viewContentService.regenerateText(requestPayload).subscribe({
      next: (response: any) => {
        console.log('Regeneration Response:', response);
        this.regeneratedText = response.regeneratedText;
        this.isModalVisible = true;
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error regenerating text:', error);
        console.error('Error details:', {
          status: error.status,
          statusText: error.statusText,
          message: error.message,
          error: error.error
        });
        
        let errorMessage = 'Failed to regenerate content. ';
        if (error.error?.message) {
          errorMessage += error.error.message;
        } else if (error.status === 500) {
          errorMessage += 'Internal server error occurred.';
        }
        
        alert(errorMessage);
      }
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
    try {
      // Initialize PDF document
      const pdf = new jsPDF();
      
      // Set initial variables for formatting
      const pageWidth = pdf.internal.pageSize.getWidth();
      const margin = 20;
      const contentWidth = pageWidth - (2 * margin);
      let yPosition = 20;
  
      // Add title with null check
      pdf.setFontSize(20);
      pdf.setFont('helvetica', 'bold');
      const title = this.courseName || 'Course Content';
      pdf.text(title, pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 20;
  
      // Check if units exist
      if (!this.units || this.units.length === 0) {
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'normal');
        pdf.text('No content available', margin, yPosition);
        pdf.save('empty_course.pdf');
        return;
      }
  
      // Process each unit
      this.units.forEach((unit, index) => {
        // Check if we need a new page for the unit
        if (yPosition > 270) {
          pdf.addPage();
          yPosition = 20;
        }
  
        // Add unit header
        pdf.setFontSize(16);
        pdf.setFont('helvetica', 'bold');
        const unitHeader = `Unit ${index + 1}: ${unit.unitName || 'Untitled Unit'}`;
        pdf.text(unitHeader, margin, yPosition);
        yPosition += 10;
  
        // Add unit content with proper text wrapping
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'normal');
        
        // Handle null or undefined content
        const content = unit.content || 'No content available';
        
        // Split content into paragraphs
        const paragraphs = content.split('\n').filter((p: string) => p.trim());
        
        paragraphs.forEach((paragraph: string) => {
          // Split paragraph into lines that fit the page width
          const lines: string[] = pdf.splitTextToSize(paragraph, contentWidth);
          
          lines.forEach((line: string) => {
            // Check if we need a new page
            if (yPosition > 270) {
              pdf.addPage();
              yPosition = 20;
            }
            
            // Add the line of text
            pdf.text(line, margin, yPosition);
            yPosition += 7; // Line spacing
          });
          
          yPosition += 5; // Paragraph spacing
        });
  
        yPosition += 10; // Space between units
      });
  
      // Generate filename with sanitization
      const filename = `${(this.courseName || 'course').replace(/[^a-z0-9]/gi, '_').toLowerCase()}_content.pdf`;
      
      // Save the PDF
      pdf.save(filename);
  
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('There was an error generating the PDF. Please try again.');
    }
  }

  toggleRegeneratePopup(): void {
    this.showModifyFields = !this.showModifyFields;
  }

  // Close popup without submitting
  closePopup(): void {
    this.showModifyFields = false;
    this.regenerationReason = '';
  }

  submitReason(): void {
    if (this.regenerationReason.trim()) {
      console.log('Reason for Re-Generation:', this.regenerationReason);

      // You can pass this reason to a backend service here
      // Example:
      // this.viewContentService.submitRegenerationReason(this.regenerationReason).subscribe(response => {
      //   console.log('Regeneration reason submitted successfully', response);
      // });

      alert('Thank you for providing the reason.');
      this.closePopup();
    } else {
      alert('Please provide a reason before submitting.');
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