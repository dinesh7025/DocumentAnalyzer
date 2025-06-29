// src/app/services/document.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DocumentModel } from '../models/document-model';

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private BASE_URL = 'http://127.0.0.1:5000/api';

  constructor(private http: HttpClient) {}

  // Get all documents (Admin)
  getAllDocuments(): Observable<DocumentModel[]> {
    return this.http.get<DocumentModel[]>(`${this.BASE_URL}/documents`);
  }

  // Get documents by user ID
  getDocumentsByUser(userId: number): Observable<DocumentModel[]> {
    return this.http.get<DocumentModel[]>(`${this.BASE_URL}/documents/${userId}`);
  }

  // Upload document
  uploadDocument(file: File, userId: number): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('userId', userId.toString());
    return this.http.post(`${this.BASE_URL}/upload`, formData, {
      reportProgress: true,
      observe: 'events'
    });
  }

  // Reprocess a document
  reprocessDocument(docId: number): Observable<any> {
    return this.http.post(`${this.BASE_URL}/documents/${docId}/reprocess`, {});
  }

  // Route document to a specific type
  routeDocument(docId: number, docType: string): Observable<any> {
    return this.http.post(`${this.BASE_URL}/documents/${docId}/route-to`, {
      doc_type: docType
    });
  }

  // Delete a document
  deleteDocument(documentId: number): Observable<any> {
    return this.http.delete(`${this.BASE_URL}/documents/${documentId}`);
  }
saveEmailCredentials(user_id: number, app_email: string, app_password: string): Observable<any> {
  return this.http.post(`${this.BASE_URL}/users/save-app-credentials`, {
    user_id,
    app_email,
    app_password
  });
}


// Use saved credentials from backend
fetchEmail(user_id: number): Observable<any> {
  return this.http.post(`${this.BASE_URL}/fetch-email`, { user_id });
}
clearEmailCredentials(user_id: number): Observable<any> {
  return this.http.post(`${this.BASE_URL}/users/clear-app-credentials`, { user_id });
}


}