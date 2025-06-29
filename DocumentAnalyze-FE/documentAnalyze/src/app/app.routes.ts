import { Routes } from '@angular/router';
import { AuthComponent } from './components/auth-component/auth-component';
import { DashboardLayout } from './components/dashboard-layout/dashboard-layout';
import { DocumentListComponent } from './components/documents/document-list/document-list';
import { UploadDialogComponent } from './components/documents/upload-dialog/upload-dialog';
import { AuthGuard } from './guard/auth.guard-guard';
import { HomeComponent } from './pages/home/home';

export const routes: Routes = [
    { path: '', component: HomeComponent },
    { path: 'login', component: AuthComponent},
    {
        path: 'dashboard',
        component: DashboardLayout,
        canActivate: [AuthGuard],
        children: [
          { path: '', redirectTo: 'documents', pathMatch: 'full' },
          { path: 'documents', component: DocumentListComponent },
          { path: 'upload', component: UploadDialogComponent }
        ]
      },
    { path: '**', redirectTo: '' }
];
