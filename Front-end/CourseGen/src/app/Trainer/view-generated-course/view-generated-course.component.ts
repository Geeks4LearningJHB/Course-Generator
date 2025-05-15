import { Component, HostListener } from '@angular/core';
import { GenerateContentService } from '../../Services/generate-content.service';
import { Router } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ContentParserService } from '../../Services/content-parser.service';
import { Unit, ViewContentService } from '../../Services/view-content.service';
import { ParsedUnit, UnitWithContent } from '../../interface/unit.interfaces';
import { UnitMapper } from '../../utils/unit-mapper';

@Component({
  selector: 'app-view-generated-course',
  templateUrl: './view-generated-course.component.html',
  styleUrl: './view-generated-course.component.css',
})
export class ViewGeneratedCourseComponent {
  generatedCourse: any = null;
  parsedUnits: ParsedUnit[] = [];
  units: UnitWithContent[] = [];
  isCollapsed = true;
  expandedUnits: { [key: string]: boolean } = {};
  loadedUnits: Set<number> = new Set();
  currentPage: number = 1;
  itemsPerPage: number = 5; // Number of units displayed per page
  isLoading: { [key: string]: boolean } = {};
  isRegenerateModalVisible: boolean = false;
  isModalVisible: boolean = false;
  // selectedUnit: string = '';
  reason: string = '';
  // units: Unit[] = [];
  regenerationReason: string = '';
  selectedUnit: string | null = null;
  selectedUnits: UnitWithContent  | null = null;
  isRegenerating: boolean = false;
  currentModuleId: string = '';

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
    
    if (this.generatedCourse?.module?.moduleId) {
      this.currentModuleId = this.generatedCourse.module.moduleId;
      console.log('Module ID set:', this.currentModuleId);
    }
    
    if (this.generatedCourse?.units) {
      this.parsedUnits = this.generatedCourse.units.map((unit: any, index: number) => ({
        unitId: unit.unitId,
        unitName: unit.unitName,
        unitDescription: unit.unitDescription || '',
        duration: unit.duration || 0,
        content: unit.content || '',
        unitNum: index + 1,
        title: unit.unitName,
        introduction: '',
        keyConcepts: [],
        sections: [],
        isLoaded: false
      }));

      this.units = this.parsedUnits.map(unit => UnitMapper.parsedUnitToUnit(unit));

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

  openRegenerateForm(unit: ParsedUnit | UnitWithContent): void {
    const unitWithContent = 'unitId' in unit 
      ? unit as UnitWithContent 
      : UnitMapper.parsedUnitToUnit(unit);
      
    console.log('Opening regenerate form for unit:', unitWithContent);
    this.selectedUnit = unitWithContent.unitId;
    this.selectedUnits = unitWithContent;
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
    if (!this.selectedUnits || !this.regenerationReason || !this.currentModuleId) {
      alert('Please provide a valid reason for regeneration.');
      return;
    }
  
    this.isRegenerating = true;
  
    const payload = {
      moduleId: this.currentModuleId,
      unitId: this.selectedUnits.unitId,
      reason: this.regenerationReason
    };
  
    console.log('Regeneration payload:', payload);

    this.viewContentService.regenerateUnit(payload).subscribe({
      next: (response) => {
        console.log('Regeneration successful:', response);
        if (response.regeneratedContent) {
          const unitIndex = this.units.findIndex(u => u.unitId === this.selectedUnits?.unitId);
          if (unitIndex !== -1) {
            this.units[unitIndex].content = response.regeneratedContent;
            // Also update the parsed units if needed
            this.parsedUnits[unitIndex] = {
              ...this.parsedUnits[unitIndex],
              ...UnitMapper.unitToParsedUnit(this.units[unitIndex])
            };
          }
        }
        this.isRegenerating = false;
        alert('Unit regenerated successfully!');
        this.closeRegenerateForm();
      },
      error: (error) => {
        console.error('Full error details:', error);
        this.isRegenerating = false;
        let errorMessage = 'Failed to regenerate unit: ';
        
        if (error.error?.error) {
          errorMessage += error.error.error;
        } else if (error.message) {
          errorMessage += error.message;
        } else {
          errorMessage += 'Unknown error occurred';
        }
        
        alert(errorMessage);
      },
      complete: () => {
        this.isRegenerating = false;
      }
    });
  }
}
