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
  
  export interface UnitWithContent extends ParsedUnit {
    unitId: string;
    unitName: string;
    unitDescription: string;
    duration: number;
    content?: string;
  }