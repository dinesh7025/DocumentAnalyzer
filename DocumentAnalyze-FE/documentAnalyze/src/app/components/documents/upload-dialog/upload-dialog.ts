import { Component } from '@angular/core';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { DocumentService } from '../../../services/document-service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { MatIconButton } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';

@Component({
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatIconButton, MatIconModule, MatProgressBarModule],
  selector: 'app-upload-dialog',
  templateUrl: './upload-dialog.html',
  styleUrls: ['./upload-dialog.css']
})
export class UploadDialogComponent {
  selectedFile: File | null = null;
  dragOver = false;
  uploadProgress = 0;
  uploading = false;

  constructor(
    private dialogRef: MatDialogRef<UploadDialogComponent>,
    private docService: DocumentService,
    private snackBar: MatSnackBar
  ) {}

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input?.files?.length) {
      const file = input.files[0];
      this.validateAndSetFile(file);
    }
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.dragOver = false;
    if (event.dataTransfer?.files?.length) {
      this.validateAndSetFile(event.dataTransfer.files[0]);
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.dragOver = true;
  }

  onDragLeave() {
    this.dragOver = false;
  }

  validateAndSetFile(file: File) {
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      this.snackBar.open('Only PDF, JPG, and PNG files are allowed.', 'Close', { duration: 3000 });
      return;
    }
    this.selectedFile = file;
  }

  upload() {
    if (!this.selectedFile) return;

    const user = JSON.parse(localStorage.getItem('user') || '{}');


    this.uploading = true;

    this.docService.uploadDocument(this.selectedFile,user?.user_id).subscribe({
      next: (event: HttpEvent<any>) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.uploadProgress = Math.round((event.loaded / event.total) * 100);
        } else if (event.type === HttpEventType.Response) {
          this.snackBar.open('Upload successful!', 'Close', { duration: 3000 });
          this.dialogRef.close('uploaded');
        }
      },
      error: err => {
        this.uploading = false;
        this.snackBar.open('Upload failed. Please try again.', 'Close', { duration: 3000 });
      }
    });
  }

  close() {
    this.dialogRef.close();
  }
}
