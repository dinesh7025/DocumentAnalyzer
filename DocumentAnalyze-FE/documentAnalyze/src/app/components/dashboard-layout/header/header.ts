import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';


@Component({
  standalone: true,
  imports: [CommonModule],
  selector: 'app-header',
  templateUrl: './header.html',
  styleUrls: ['./header.css']
})
export class HeaderComponent implements OnInit {
  username: string = '';

  constructor(private router: Router) {}

  ngOnInit(): void {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    this.username = user?.username || 'Guest';
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}
