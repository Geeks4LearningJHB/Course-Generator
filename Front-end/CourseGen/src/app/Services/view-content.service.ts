import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Unit {
  unitId: string;
  unitName: string;
  unitDescription: string;
  duration: number;
  content: string;
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



@Injectable({
  providedIn: 'root'
})
export class ViewContentService {

  private apiUrl = 'http://localhost:8080/AI';

  constructor(private http: HttpClient) { }

  getAllUnits(): Observable<Unit[]> {
    return this.http.get<Unit[]>(this.apiUrl + '/getAllUnits');
  }

  getUnitsByModules(moduleId: string): Observable<Unit[]> {
    console.log('Fetching units for moduleId:', moduleId);
    return this.http.get<Unit[]>(`${this.apiUrl}/getUnitsByModules?moduleId=${moduleId}`);
  }
  
  

  // http://localhost:8080/AI/getUnitsByModules?moduleId=67515f581f4a723ec0b0dfc5
}
