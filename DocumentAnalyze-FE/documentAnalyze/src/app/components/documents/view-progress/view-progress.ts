import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { NgClass } from '@angular/common';

@Component({
  selector: 'app-view-progress',
  imports: [CommonModule, MatButtonModule, MatTooltipModule, NgClass],
  templateUrl: './view-progress.html',
  styleUrl: './view-progress.css'
})
export class ViewProgress {
  constructor(
    public dialogRef: MatDialogRef<ViewProgress>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  close(): void {
    this.dialogRef.close();
  }

  getStage(name: string): any | null {
    return this.data?.stages?.find((s: any) => s.name === name) || null;
  }

  getConfidencePercent(confidence: string | number): string {
    const value = typeof confidence === 'string' ? parseFloat(confidence) : confidence;
    return (value * 100).toFixed(0) + '%';
  }
}
