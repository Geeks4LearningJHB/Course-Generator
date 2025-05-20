export interface ListItem {
  text?: string;
  subItems?: string[];
  language?: string;
  code?: string;
}

export interface OriginalContent {
  explanation?: string;
  examples?: string[];
}

export interface ParsedSection {
  heading: string;
  content: string | ListItem[];
}

export interface ParsedUnit {
  unitId: string;
  unitName: string;
  unitDescription: string;
  content: string;
  unitNum: number;
  title: string;
  introduction: string;
  keyConcepts: string[];
  sections: ParsedSection[];
  type: string;
  isLoaded: boolean;
  originalContent?: OriginalContent;
}

export interface UnitWithContent {
  unitId: string;
  unitName: string;
  unitDescription?: string;
  content: string;
  type?: string;
  unitNum: number;
  originalContent?: OriginalContent;
}

export interface UnitSection {
  heading: string;
  content: string | string[] | { language: string; code: string }[];
}

export interface RegenerationRequest {
  moduleId: string;
  unitId: string;
  reason: string;
}

export interface RegenerationResponse {
  success: boolean;
  regeneratedContent: string;
  message?: string;
}