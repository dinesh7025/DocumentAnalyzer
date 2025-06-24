import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { UploadDialogComponent } from '../../documents/upload-dialog/upload-dialog';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import {MatListModule} from '@angular/material/list'

@Component({
  standalone: true,
  imports: [CommonModule, MatIconModule, MatListModule],
  selector: 'app-sidebar',
  templateUrl: './sidebar.html',
  styleUrls: ['./sidebar.css']
})
export class SidebarComponent {
  constructor(private dialog: MatDialog) {}

  openUpload() {
    this.dialog.open(UploadDialogComponent, {
      width: '400px'
    });
  }
}
