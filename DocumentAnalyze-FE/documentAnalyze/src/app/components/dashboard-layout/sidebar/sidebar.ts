import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { UploadDialogComponent } from '../../documents/upload-dialog/upload-dialog';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { MatListModule } from '@angular/material/list';
import { EmailDialogComponent } from '../sidebar/email-dialog/email-dialog';
import { DocumentService } from '../../../services/document-service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  standalone: true,
  imports: [CommonModule, MatIconModule, MatListModule],
  selector: 'app-sidebar',
  templateUrl: './sidebar.html',
  styleUrls: ['./sidebar.css'],
})
export class SidebarComponent implements OnInit {
  hasEmailCredentials: boolean = false;

  constructor(
    private dialog: MatDialog,
    private documentService: DocumentService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.updateEmailCredentialStatus();
  }

  openUpload() {
    this.dialog.open(UploadDialogComponent, {
      width: '400px'
    });
  }

  updateEmailCredentialStatus() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    this.hasEmailCredentials = !!(user.app_email && user.app_password);
  }

  checkEmail() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    if (!user || !user.user_id) {
      this.snackBar.open('User not found in local storage.', 'Close', { duration: 3000 });
      return;
    }

    if (!user.app_email || !user.app_password) {
      const dialogRef = this.dialog.open(EmailDialogComponent, { width: '400px' });

      dialogRef.afterClosed().subscribe(result => {
        if (result?.app_email && result?.app_password) {
          this.documentService.saveEmailCredentials(user.user_id, result.app_email, result.app_password)
            .subscribe(() => {
              user.app_email = result.app_email;
              user.app_password = result.app_password;
              localStorage.setItem('user', JSON.stringify(user));
              this.updateEmailCredentialStatus();
              this.fetchEmailFromServer();
            }, () => {
              this.snackBar.open('Failed to save credentials.', 'Close', { duration: 3000 });
            });
        }
      });
    } else {
      this.fetchEmailFromServer();
    }
  }

  fetchEmailFromServer() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    if (!user || !user.user_id) {
      this.snackBar.open('User ID not found. Cannot fetch emails.', 'Close', { duration: 3000 });
      return;
    }

    this.documentService.fetchEmail(user.user_id).subscribe({
      next: (res: any) => {
        console.log('Email fetch successful:', res);
        this.snackBar.open(res.message || 'Email fetched successfully.', 'Close', { duration: 3000 });
      },
      error: (err: any) => {
        console.error('Email fetch error:', err);
        const errorMessage = err.error?.error || 'Failed to fetch email.';
        this.snackBar.open(errorMessage, 'Close', { duration: 5000 });

        if (errorMessage.includes("No saved email credentials found") ||
            errorMessage.includes("Please check your email credentials.")) {
          user.app_email = null;
          user.app_password = null;
          localStorage.setItem('user', JSON.stringify(user));
          this.updateEmailCredentialStatus();
          this.snackBar.open('Saved email credentials are invalid. Please re-enter them.', 'Close', { duration: 5000 });
        }
      }
    });
  }

  signOutEmail() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    if (!user.user_id) {
      this.snackBar.open('User ID not found.', 'Close', { duration: 3000 });
      return;
    }

    this.documentService.clearEmailCredentials(user.user_id).subscribe(() => {
      user.app_email = null;
      user.app_password = null;
      localStorage.setItem('user', JSON.stringify(user));
      this.updateEmailCredentialStatus();
      this.snackBar.open('App email/password cleared.', 'Close', { duration: 3000 });
    }, () => {
      this.snackBar.open('Failed to clear credentials.', 'Close', { duration: 3000 });
    });
  }
}
