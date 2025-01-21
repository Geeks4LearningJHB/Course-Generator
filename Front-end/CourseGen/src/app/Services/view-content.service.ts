import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Unit {
  unitId: string;
  unitName: string;
  unitDescription: string;
  duration: number;
  content: string ;
  unitNum: number;
  isExpanded?: boolean;
  isLoaded?: boolean;
  moduleName?: string;
  title?: string;
  introduction?: string;
  keyConcepts?: string[];
  sections?: Section[];
}

export interface Section {
  heading: string;
  content: string | ListItem[];
}

export interface ListItem {
  text?: string;
  subItems?: string[];
  language?: string;
  code?: string;
}


export interface RegenerateRequest {
  moduleId: string;
  unitId: string;
  highlightedText: string;
  startIndex: number;
  endIndex: number;
}

export interface UpdateRequest {
  unitId: string;
  regeneratedText: string;
  startIndex: number;
  endIndex: number;
}

@Injectable({
  providedIn: 'root'
})
export class ViewContentService {

 
  private apiUrl = 'http://localhost:8080/AI';

  constructor(private http: HttpClient) { }

  getAllUnits(): Observable<Unit[]> {
    return this.http.get<Unit[]>(`${this.apiUrl}/getAllUnits`);
  }

  regenerateUnit(payload: { unitId: string; reason: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/regenerateUnitWithReason`, payload);
  }
  
  
  // http://localhost:8080/AI/regenerateUnitWithReason

  getUnitsByModules(moduleId: string): Observable<Unit[]> {
    console.log('Fetching units for moduleId:', moduleId);
    return this.http.get<Unit[]>(`${this.apiUrl}/getUnitsByModules?moduleId=${moduleId}`);
  }

  regenerateText(payload: { highlightedText: string; moduleId: string; unitId: string }) {
    return this.http.post('http://localhost:8080/AI/regenerateText', payload);
  }
  // http://localhost:8080/AI/regenerateText

  confirmUpdate(request: UpdateRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/confirmUpdate`, request);
  }
}