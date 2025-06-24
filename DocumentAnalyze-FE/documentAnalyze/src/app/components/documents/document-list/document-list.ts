// src/app/components/documents/document-list.component.ts
import { Component, OnInit, ViewChild } from '@angular/core';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatDialog } from '@angular/material/dialog';
import { DocumentService, DocumentModel } from '../../../services/document-service';
import { UploadDialogComponent } from '../upload-dialog/upload-dialog';
import { CommonModule, DatePipe } from '@angular/common';
import { MatButtonModule, MatIconButton } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

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
    MatButtonModule
  ],
  providers: [DatePipe],
  templateUrl: './document-list.html',
  styleUrls: ['./document-list.css']
})
export class DocumentListComponent implements OnInit {
  displayedColumns: string[] = ['id', 'filename', 'type', 'routed', 'time', 'status', 'actions'];
  dataSource = new MatTableDataSource<DocumentModel>();
  isAdmin = false;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private dialog: MatDialog, private docService: DocumentService) {}

  ngOnInit() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    this.isAdmin = user?.role === 'admin';

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
      if (result === 'uploaded') this.ngOnInit();
    });
  }

  deleteDocument(id: number) {
    if (confirm('Are you sure you want to delete this document?')) {
      this.docService.deleteDocument(id).subscribe(() => this.ngOnInit());
    }
  }

  downloadDocument(path: string) {
    window.open(path, '_blank');
  }
}
