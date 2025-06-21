import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-landing',
  imports: [MatButtonModule, MatCardModule,CommonModule],
  templateUrl: './landing.html',
  styleUrl: './landing.css'
})
export class LandingComponent {
  features = [
    { title: 'Auto-Classification', description: 'Let AI identify document types instantly.' },
    { title: 'Smart Routing', description: 'Documents are routed automatically to the right system.' },
    { title: 'Secure Uploads', description: 'All files are encrypted and securely stored in Azure.' }
  ];
}
