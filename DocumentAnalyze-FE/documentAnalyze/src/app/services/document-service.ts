// src/app/services/document.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
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

  reprocessDocument(docId: number): Observable<any> {
    return this.http.post(`${this.BASE_URL}/documents/${docId}/reprocess`, {});
  }

  routeDocument(docId: number, docType: string): Observable<any> {
  return this.http.post(`${this.BASE_URL}/documents/${docId}/route-to`, {
    doc_type: docType
  });
}

    
  // Delete document
  deleteDocument(documentId: number): Observable<any> {
    return this.http.delete(`${this.BASE_URL}/documents/${documentId}`);
  }
}
