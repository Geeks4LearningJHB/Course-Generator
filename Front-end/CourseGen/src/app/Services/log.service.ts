import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface LogEntry {
  userId: number;
  action: string;
  timestamp: string;
}

@Injectable({
  providedIn: 'root'
})
export class LogService {
  private apiUrl = 'http://localhost:8080/api/logs'; 

  constructor(private http: HttpClient) {}

  // Get all logs
  getLogs(): Observable<LogEntry[]> {
    return this.http.get<LogEntry[]>(this.apiUrl);
  }

  // Post a new log
  postLog(entry: LogEntry): Observable<LogEntry> {
    return this.http.post<LogEntry>(this.apiUrl, entry);
  }
}
