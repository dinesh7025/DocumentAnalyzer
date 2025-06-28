import { Component, Inject } from '@angular/core';
import { MatDialogActions, MatDialogContent, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormField, MatLabel, MatOption, MatSelect } from '@angular/material/select';

@Component({
  selector: 'app-route-dialog',
  imports: [MatDialogContent, MatDialogActions,MatOption, MatSelect, MatLabel, MatFormField],
  templateUrl: './route-dialog.html',
  styleUrl: './route-dialog.css'
})
export class RouteDialog {
  selectedType: string = '';

  constructor(
    public dialogRef: MatDialogRef<RouteDialog>,
    @Inject(MAT_DIALOG_DATA) public data: { docId: number }
  ) {}

  onCancel(): void {
    this.dialogRef.close();
  }

  onConfirm(): void {
    this.dialogRef.close(this.selectedType);
  }
}
