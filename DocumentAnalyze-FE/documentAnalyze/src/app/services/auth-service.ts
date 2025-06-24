import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

const BASE_URL = 'http://localhost:5000/api/auth';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(private http: HttpClient) {}

  login(credentials: { username: string, password: string }): Observable<any> {
    return this.http.post(`${BASE_URL}/login`, credentials);
  }

  signup(userData: { username: string, password: string, email: string }): Observable<any> {
    return this.http.post(`${BASE_URL}/signup`, userData);
  }
}
