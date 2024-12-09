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
  

  // http://localhost:8080/AI/getUnitsByModules?moduleId=67504e80529d2d3c6344ad21
}
