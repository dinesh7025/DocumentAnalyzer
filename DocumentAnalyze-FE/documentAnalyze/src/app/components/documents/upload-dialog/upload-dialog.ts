import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DocumentService } from '../../../services/document-service';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatButtonModule } from '@angular/material/button';

@Component({
  standalone: true,
  selector: 'app-upload-dialog',
  templateUrl: './upload-dialog.html',
  styleUrls: ['./upload-dialog.css'],
  imports: [
    CommonModule,
    MatDialogModule,
    MatIconModule,
    MatProgressBarModule,
    MatButtonModule
  ]
})
export class UploadDialogComponent {
  selectedFiles: File[] = [];
  uploadProgressMap = new Map<string, number>();
  dragOver = false;
  uploading = false;

  constructor(
    private dialogRef: MatDialogRef<UploadDialogComponent>,
    private docService: DocumentService,
    private snackBar: MatSnackBar
  ) {}

  onFilesSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input?.files?.length) {
      this.addFiles(Array.from(input.files));
    }
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.dragOver = false;
    if (event.dataTransfer?.files?.length) {
      this.addFiles(Array.from(event.dataTransfer.files));
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.dragOver = true;
  }

  onDragLeave() {
    this.dragOver = false;
  }

  addFiles(files: File[]) {
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    for (const file of files) {
      if (!allowedTypes.includes(file.type)) {
        this.snackBar.open(`File "${file.name}" is not a supported format.`, 'Close', { duration: 3000 });
        continue;
      }
      if (!this.selectedFiles.some(f => f.name === file.name)) {
        this.selectedFiles.push(file);
      }
    }
  }

  upload() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (!this.selectedFiles.length) return;

    this.uploading = true;

    const uploads = this.selectedFiles.map(file =>
      this.docService.uploadDocument(file, user?.user_id).subscribe({
        next: (event: HttpEvent<any>) => {
          if (event.type === HttpEventType.UploadProgress && event.total) {
            const percent = Math.round((event.loaded / event.total) * 100);
            this.uploadProgressMap.set(file.name, percent);
          } else if (event.type === HttpEventType.Response) {
            this.uploadProgressMap.set(file.name, 100);
          }
        },
        error: () => {
          this.snackBar.open(`Upload failed for ${file.name}`, 'Close', { duration: 3000 });
          this.uploadProgressMap.set(file.name, -1);
        }
      })
    );

    // Close dialog after uploads
    Promise.allSettled(uploads).then(() => {
      this.snackBar.open('All uploads attempted.', 'Close', { duration: 3000 });
      this.dialogRef.close('uploaded');
    });
  }

  close() {
    this.dialogRef.close();
  }

  removeFile(index: number) {
    this.selectedFiles.splice(index, 1);
  }

  getUploadProgress(fileName: string): number {
    return this.uploadProgressMap.get(fileName) || 0;
  }

  isFailed(fileName: string): boolean {
    return this.uploadProgressMap.get(fileName) === -1;
  }
}
