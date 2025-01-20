import { Component, HostListener } from '@angular/core';
import { GenerateContentService } from '../../Services/generate-content.service';
import { Router } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ContentParserService } from '../../Services/content-parser.service';
import { Unit, ViewContentService } from '../../Services/view-content.service';

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
  selector: 'app-view-generated-course',
  templateUrl: './view-generated-course.component.html',
  styleUrl: './view-generated-course.component.css',
})
export class ViewGeneratedCourseComponent {
  generatedCourse: any = null;
  parsedUnits: ParsedUnit[] = [];
  isCollapsed = true;
  expandedUnits: { [key: string]: boolean } = {};
  loadedUnits: Set<number> = new Set();
  currentPage: number = 1;
  itemsPerPage: number = 5; // Number of units displayed per page
  isLoading: { [key: string]: boolean } = {};
  isRegenerateModalVisible: boolean = false;
  isModalVisible: boolean = false;
  selectedUnit: string = '';
  reason: string = '';
  units: Unit[] = [];

  constructor(
    private router: Router,
    private generateContentService: GenerateContentService,
    private contentParserService: ContentParserService,
    private viewContentService: ViewContentService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit() {
    this.generatedCourse = this.generateContentService.getGeneratedCourse();
    console.log(this.generatedCourse);
    
    if (this.generatedCourse?.units) {
      console.log(this.generatedCourse?.units);
      // Initialize units with minimal data
      this.parsedUnits = this.generatedCourse.units.map((unit: any, index: number) => ({
        monthNumber: index + 1,
        title: unit.unitName,
        introduction: '',
        keyConcepts: [],
        sections: [],
        isLoaded: false
      }));

      // Initialize expansion state
      this.generatedCourse.units.forEach((unit: any) => {
        this.expandedUnits[unit.unitName] = false;
      });
    }
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

  async loadUnitContent(globalIndex: number): Promise<void> {
    try {
      const unit = this.generatedCourse.units[globalIndex];
      if (!unit?.content) return;
  
      const parsedContent = await this.contentParserService.parseContent(
        unit.content,
        1000 // chunk size
      );
  
      if (parsedContent.length > 0) {
        this.parsedUnits[globalIndex] = {
          ...this.parsedUnits[globalIndex],
          ...parsedContent[0],
          isLoaded: true
        };
      }
    } catch (error) {
      console.error('Error loading unit:', error);
    }
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
  
  onSubmit() {
    const requestBody = {
      unitId: this.selectedUnit,
      reason: this.reason,
    };

    this.viewContentService.regenerateUnit(requestBody).subscribe(
      (response) => {
        console.log('Unit regeneration successful!', response);
        this.isModalVisible = false; // Hide modal after success
        // You can add additional logic to notify the user of success
      },
      (error) => {
        console.error('Error regenerating unit', error);
        // Add additional error handling logic as needed
      }
    );
  }

  async toggleUnit(unitTitle: string, index: number): Promise<void> {
    this.expandedUnits[unitTitle] = !this.expandedUnits[unitTitle];
    
    // Calculate the global index considering pagination
    const globalIndex = (this.currentPage - 1) * this.itemsPerPage + index;
    
    if (this.expandedUnits[unitTitle] && !this.parsedUnits[globalIndex]?.isLoaded) {
      this.isLoading[unitTitle] = true;
      try {
        await this.loadUnitContent(globalIndex);
      } finally {
        this.isLoading[unitTitle] = false;
      }
    }
  }
  

  onEditCourse() {
    this.isRegenerateModalVisible = true;
  }

  saveCourse() {
    this.generateContentService
      .saveGeneratedCourse(this.generatedCourse)
      .subscribe(
        (response) => {
          alert('Course saved successfully!');
          this.router.navigate(['/dashboard']);
        },
        (error) => {
          alert('Failed to save course.');
        }
      );
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
}
