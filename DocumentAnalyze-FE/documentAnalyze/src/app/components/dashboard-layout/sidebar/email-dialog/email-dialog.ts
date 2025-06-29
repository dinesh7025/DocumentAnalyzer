import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';

@Component({
  selector: 'app-email-dialog',
  standalone: true,
  templateUrl: './email-dialog.html',
  styleUrls: ['./email-dialog.css'],
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatDialogModule
  ]
})
export class EmailDialogComponent {
  app_email = '';
  app_password = '';

  constructor(private dialogRef: MatDialogRef<EmailDialogComponent>) {}

  submit() {
    this.dialogRef.close({
      app_email: this.app_email,
      app_password: this.app_password
    });
  }

  close() {
    this.dialogRef.close();
  }
}
