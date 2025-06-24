import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './header/header';
import { SidebarComponent } from './sidebar/sidebar';

@Component({
  selector: 'app-dashboard-layout',
  imports: [RouterOutlet, HeaderComponent, SidebarComponent],
  templateUrl: './dashboard-layout.html',
  styleUrl: './dashboard-layout.css'
})
export class DashboardLayout {

}
