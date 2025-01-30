import { Component, HostListener, OnInit, AfterViewInit } from '@angular/core';
import { Unit, ViewContentService } from '../../Services/view-content.service';
import {
  Course,
  ViewCoursesService,
} from '../../Services/view-courses.service';
import { ToggleService } from '../../Services/toggle.service';
import { ActivatedRoute, Router } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { ContentParserService } from '../../Services/content-parser.service';
import { GenerateContentService } from '../../Services/generate-content.service';
import { forkJoin } from 'rxjs';

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
  monthNumber: number;
  title: string;
  introduction: string;
  keyConcepts: string[];
  sections: ParsedSection[];
  isLoaded?: boolean;
}

@Component({
  selector: 'app-view-content',
  templateUrl: './view-content.component.html',
  styleUrls: ['./view-content.component.css'],
})
export class ViewContentComponent implements OnInit, AfterViewInit {
  showModifyFields: boolean = false;
  module: string = '';
  topic: string = '';
  details: string = '';
  isCollapsed = true;
  units: Unit[] = [];
  unit: any[] = [];
  courses: Course[] = [];
  course: Course | undefined;
  selectedCourse: Course | null = null;
  generatedData: any;
  courseName: string = '';
  currentCourseId: string = '';
  regenerationReason: string = '';
  selectedUnit: string | null = null;
  selectedUnits: Unit | null = null;
  reason: string = '';
  generatedCourse: any = null;
  parsedUnits: ParsedUnit[] = [];
  expandedUnits: { [key: string]: boolean } = {};
  loadedUnits: Set<number> = new Set();
  currentPage: number = 1;
  itemsPerPage: number = 5; // Number of units displayed per page
  isLoading: { [key: string]: boolean } = {};
  isRegenerating: boolean = false;

  // Variables for highlighted text and floating button
  highlightedText: string = '';
  showFloatingButton: boolean = false;
  // highlightedTextRange: any = null;
  buttonPosition: { top: string; left: string } = { top: '0px', left: '0px' }; // Define button position
  isModalVisible: boolean = false;
  isRegenerateModalVisible: boolean = false;
  selectedText: string = '';
  regeneratedText: string = '';
  currentUnit: Unit | null = null;

  constructor(
    private router: Router,
    private viewContentService: ViewContentService,
    private route: ActivatedRoute,
    private viewCoursesService: ViewCoursesService,
    private generateContentService: GenerateContentService,
    private http: HttpClient,
    private toggleService: ToggleService,
    private contentParserService: ContentParserService,
    private sanitizer: DomSanitizer
  ) {
    // const nav = this.router.getCurrentNavigation();
    // this.generatedData = nav?.extras.state?.['data'];
  }

  ngAfterViewInit(): void {
    const unitElements = document.querySelectorAll('.unit-card');
    if (unitElements.length === 0) {
      console.warn('No Unit Elements found.');
    } else {
      unitElements.forEach((unitElement) => {
        // console.log('Unit Element found:', unitElement);
        unitElement.addEventListener('click', () => {
          console.log(
            'Unit Element clicked!',
            unitElement.getAttribute('data-unit-id')
          );
          // Perform further actions, e.g., showing a modal or expanding content
        });
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
    this.toggleService.isCollapsed$.subscribe(
      (collapsed) => (this.isCollapsed = collapsed)
    );

    // this.generatedCourse = this.courses.moduleName;
  }

  get paginatedUnits() {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    return this.parsedUnits.slice(startIndex, endIndex);
  }

  get totalPages(): number {
    return Math.ceil(this.parsedUnits.length / this.itemsPerPage);
  }

  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }

  previousPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  changePage(page: number): void {
    this.currentPage = page;
  }

  public parseLinksAndBold(content: string): string {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const boldRegex = /\*\*(.*?)\*\*/g;
    // Replace URLs with anchor tags
    let formattedContent = content.replace(
      urlRegex,
      '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );

    // Replace **bold** with <b>bold</b>
    formattedContent = formattedContent.replace(boldRegex, '<b>$1</b>');

    return formattedContent;
  }

  loadCourseContent(courseId: string): void {
    forkJoin({
      course: this.viewCoursesService.getModuleById(courseId),
      units: this.viewContentService.getUnitsByModules(courseId),
    }).subscribe({
      next: ({ course, units }) => {
        this.courseName = course.moduleName;
        this.selectedCourse = course;
        this.units = units.map((unit) => ({ ...unit, isExpanded: false }));
      },
      error: (err) => console.error('Error loading course content:', err),
    });
  }

  onUnitClick(unit: any): void {
    unit.isExpanded = !unit.isExpanded;
    console.log(
      `Unit ${unit.isExpanded ? 'expanded' : 'collapsed'}:`,
      unit.unitName,
      unit.unitId
    );
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.sidebar') && !target.closest('.toggle-btn')) {
      this.isCollapsed = true;
    }
  }

  isListContent(content: string | any[]): boolean {
    return Array.isArray(content);
  }

  isString(value: any): value is string {
    return typeof value === 'string';
  }

  isArray(value: any): value is Array<any> {
    return Array.isArray(value);
  }

  asArray(value: any): any[] {
    return this.isArray(value) ? value : [];
  }

  isCodeBlock(item: any): item is { language: string; code: string } {
    return (
      item && typeof item.language === 'string' && typeof item.code === 'string'
    );
  }

  hasSubItems(item: any): item is { text: string; subItems: string[] } {
    return (
      item && typeof item.text === 'string' && Array.isArray(item.subItems)
    );
  }

  sanitizeContent(content: string): SafeHtml {
    return this.sanitizer.bypassSecurityTrustHtml(content);
  }

  formatContent(content: string | any[]): SafeHtml {
    if (typeof content === 'string') {
      // Handle any HTML in the content safely
      return this.sanitizer.bypassSecurityTrustHtml(content);
    }
    // If it's not a string, convert it to a string representation
    return this.sanitizer.bypassSecurityTrustHtml(String(content));
  }

  getSectionContent(content: string | any[]): string {
    if (typeof content === 'string') {
      return content;
    }
    return JSON.stringify(content);
  }

  @HostListener('window:mouseup', ['$event'])
  onMouseUp(event: MouseEvent) {
    const selection = window.getSelection();
    console.log('Selection:', selection);

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
          console.log('Highlighted Text:', this.highlightedText);

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
      endIndex:
        this.currentUnit.content.indexOf(this.highlightedText) +
        this.highlightedText.length,
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
          error: error.error,
        });

        let errorMessage = 'Failed to regenerate content. ';
        if (error.error?.message) {
          errorMessage += error.error.message;
        } else if (error.status === 500) {
          errorMessage += 'Internal server error occurred.';
        }

        alert(errorMessage);
      },
    });
  }

  confirmUpdate() {
    if (!this.currentUnit || !this.highlightedText || !this.regeneratedText) {
      alert('Something went wrong. Please try again.');
      return;
    }
  
    // Find the start index of the highlighted text
    const startIndex = this.currentUnit.content.indexOf(this.highlightedText);
    if (startIndex === -1) {
      alert('Selected text not found in the unit content.');
      return;
    }
  
    // Replace the old text with the regenerated text
    const newContent =
      this.currentUnit.content.substring(0, startIndex) +
      this.regeneratedText +
      this.currentUnit.content.substring(startIndex + this.highlightedText.length);
  
    // Update the unit's content
    this.currentUnit.content = newContent;
  
    // Hide modal and clear highlighted text
    this.isModalVisible = false;
    this.highlightedText = '';
    this.regeneratedText = '';
  
    alert('Text updated successfully!');
  }
  

  toggleUnit(unit: any): void {
    unit.isExpanded = !unit.isExpanded; // Toggle expanded state
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
      const pdf = new jsPDF();

      // Document dimensions and formatting
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 20;
      const contentWidth = pageWidth - 2 * margin;

      // Set initial position
      let yPosition = 20;

      // Add document title
      const title = this.courseName || 'Course Content';
      pdf.setFontSize(32).setFont('Bahnschrift Regular', 'bold');
      pdf.text(title, pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 20;

      // Reserve a page for the Table of Contents
      pdf.addPage(); // Add a blank page for the ToC
      const tocPage = pdf.getNumberOfPages();

      // Move to the next page for units
      pdf.addPage();
      yPosition = 20;

      // Check if there are any units
      if (!this.units || this.units.length === 0) {
        pdf.setFontSize(14).setFont('helvetica', 'italic');
        pdf.text('No content available', margin, yPosition);
        pdf.save('empty_course.pdf');
        return;
      }

      // Initialize Table of Contents array
      const tableOfContents: { unitTitle: string; pageNumber: number }[] = [];

      // Process each unit
      this.units.forEach(
        (unit: { unitName: string; content: string }, index: number) => {
          if (yPosition + 40 > pageHeight) {
            pdf.addPage();
            yPosition = 20;
          }

          // Add unit title
          const unitTitle = `Unit ${index + 1}: ${
            unit.unitName || 'Untitled Unit'
          }`;
          pdf.setFontSize(18).setFont('helvetica', 'bold');
          pdf.text(unitTitle, margin, yPosition);

          // Add entry to ToC
          tableOfContents.push({
            unitTitle,
            pageNumber: pdf.getNumberOfPages(),
          });

          yPosition += 15;

          // Add unit content
          const content = unit.content || 'No content available';
          const paragraphs = content
            .split('\n')
            .filter((p: string) => p.trim());
          pdf.setFontSize(12).setFont('helvetica', 'normal');

          paragraphs.forEach((paragraph: string) => {
            const lines: string[] = pdf.splitTextToSize(
              paragraph,
              contentWidth
            );

            lines.forEach((line: string) => {
              if (yPosition + 10 > pageHeight) {
                pdf.addPage();
                yPosition = 20;
              }
              pdf.text(line, margin, yPosition);
              yPosition += 7;
            });

            yPosition += 5; // Space after paragraph
          });

          yPosition += 10; // Space after unit
        }
      );

      // Populate the Table of Contents
      pdf.setPage(tocPage);
      yPosition = 20;
      pdf.setFontSize(20).setFont('helvetica', 'bold');
      pdf.text('Table of Contents', pageWidth / 2, yPosition, {
        align: 'center',
      });
      yPosition += 20;

      tableOfContents.forEach(({ unitTitle, pageNumber }) => {
        if (yPosition + 10 > pageHeight) {
          pdf.addPage();
          yPosition = 20;
        }
        pdf.setFontSize(12).setFont('helvetica', 'normal');
        pdf.text(
          `${unitTitle} ................ ${pageNumber}`,
          margin,
          yPosition
        );
        yPosition += 7;
      });

      // Add footer with page numbers
      const pageCount = pdf.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        pdf.setPage(i);
        pdf.setFontSize(10).setFont('helvetica', 'italic');
        pdf.text(`Page ${i} of ${pageCount}`, pageWidth / 2, pageHeight - 10, {
          align: 'center',
        });
      }

      // Save the PDF
      const filename = `${(this.courseName || 'course')
        .replace(/[^a-z0-9]/gi, '_')
        .toLowerCase()}_content.pdf`;
      pdf.save(filename);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('There was an error generating the PDF. Please try again.');
    }
  }

  closePopup(): void {
    this.showModifyFields = false; // Close the modal when cancel is clicked
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

  openRegenerateForm(unit: Unit): void {
    console.log('Opening regenerate form for unit:', unit);
    this.selectedUnit = unit.unitId;
    this.selectedUnits = unit;
    this.regenerationReason = '';
    this.isRegenerateModalVisible = true;
    console.log('Modal visibility:', this.isRegenerateModalVisible);
  }

  closeRegenerateForm(): void {
    console.log('Closing regenerate form');
    this.selectedUnit = null;
    this.selectedUnits = null;
    this.regenerationReason = '';
    this.isRegenerateModalVisible = false;
    console.log('Modal visibility:', this.isRegenerateModalVisible);
  }

  // view-content.component.ts
  submitRegenerationForm() {
    if (!this.selectedUnits || !this.regenerationReason) {
      alert('Please provide a valid reason for regeneration.');
      return;
    }
  
    this.isRegenerating = true; // Show loading overlay
  
    const payload = {
      moduleId: this.currentCourseId,
      unitId: this.selectedUnits.unitId,
      reason: this.regenerationReason
    };
  
    this.viewContentService.regenerateUnit(payload).subscribe({
      next: (response) => {
        console.log('Regeneration successful:', response);
        const unitIndex = this.units.findIndex(u => u.unitId === this.selectedUnits?.unitId);
        if (unitIndex !== -1) {
          this.units[unitIndex].content = response.regeneratedContent;
        }
        this.isRegenerating = false; // Hide loading overlay
        alert('Unit regenerated successfully!');
        this.closeRegenerateForm();
      },
      error: (error) => {
        console.error('Full error details:', error);
        this.isRegenerating = false; // Hide loading overlay
        let errorMessage = 'Failed to regenerate unit: ';
        
        if (error.error?.error) {
          errorMessage += error.error.error;
        } else if (error.message) {
          errorMessage += error.message;
        } else {
          errorMessage += 'Unknown error occurred';
        }
        
        alert(errorMessage);
      }
    });
  }
}
