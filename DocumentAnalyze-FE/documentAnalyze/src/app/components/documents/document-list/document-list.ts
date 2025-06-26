// src/app/components/documents/document-list.component.ts
import { Component, OnInit, ViewChild, OnDestroy } from '@angular/core';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatDialog } from '@angular/material/dialog';
import { DocumentService} from '../../../services/document-service';
import { UploadDialogComponent } from '../upload-dialog/upload-dialog';
import { CommonModule, DatePipe } from '@angular/common';
import { MatButtonModule, MatIconButton } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { interval, Subscription } from 'rxjs';
import { DocumentModel } from '../../../models/document-model';
import { ViewProgress } from '../view-progress/view-progress';

@Component({
  standalone: true,
  selector: 'app-document-list',
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatIconButton,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule
  ],
  providers: [DatePipe],
  templateUrl: './document-list.html',
  styleUrls: ['./document-list.css']
})
export class DocumentListComponent implements OnInit, OnDestroy {
  displayedColumns: string[] = ['id', 'filename', 'type', 'routed', 'time', 'status', 'actions'];
  dataSource = new MatTableDataSource<DocumentModel>();
  isAdmin = false;

  private pollingSubscription!: Subscription;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private dialog: MatDialog, private docService: DocumentService) {}

  ngOnInit() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    this.isAdmin = user?.role === 'admin';
    this.fetchDocuments();

    // Optional: Auto-refresh every 10 seconds
    this.pollingSubscription = interval(10000).subscribe(() => {
      this.fetchDocuments();
    });
  }

  ngOnDestroy(): void {
    if (this.pollingSubscription) {
      this.pollingSubscription.unsubscribe();
    }
  }

  fetchDocuments() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (this.isAdmin) {
      this.docService.getAllDocuments().subscribe(docs => this.setTable(docs));
    } else {
      this.docService.getDocumentsByUser(user?.user_id).subscribe(docs => this.setTable(docs));
    }
  }

  setTable(data: DocumentModel[]) {
    this.dataSource.data = data;
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  openUploadDialog() {
    const dialogRef = this.dialog.open(UploadDialogComponent, { width: '400px' });
    dialogRef.afterClosed().subscribe(result => {
      if (result === 'uploaded') {
        this.fetchDocuments(); // Only reload the table, not the whole component
      }
    });
  }
  viewProgress(doc: any): void {
    this.dialog.open(ViewProgress, {
      width: '500px',
      data: doc
    });
  }

  deleteDocument(id: number) {
    if (confirm('Are you sure you want to delete this document?')) {
      this.docService.deleteDocument(id).subscribe(() => this.fetchDocuments());
    }
  }

  downloadDocument(path: string) {
    fetch(path)
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = path.split('/').pop() || 'document';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      });
  }
  
  
}
