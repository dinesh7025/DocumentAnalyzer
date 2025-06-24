// src/app/components/auth/auth.component.ts
import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth-service';
import { ActivatedRoute, Params, Router } from '@angular/router';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './auth-component.html',
  styleUrls: ['./auth-component.css']
})
export class AuthComponent {
  authForm: FormGroup;
  isSignupMode = false;
  showSuccessMessage = false;
  showErrorMessage = false;
  errorMessage = '';
  successMessage = '';

  private route = inject(ActivatedRoute); // ✅ correct injection

  constructor(private fb: FormBuilder, private authService: AuthService, private router: Router) {
    this.authForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      email: [''] // validated only in signup
    });

    this.route.queryParams.subscribe((params: Params) => {
      this.isSignupMode = params['mode'] === 'signup';
    });
  }

  toggleMode() {
    this.isSignupMode = !this.isSignupMode;
    this.authForm.reset();
  }

  onSubmit() {
    if (this.authForm.invalid) return;

    const { username, password, email } = this.authForm.value;

    if (this.isSignupMode) {
      this.authService.signup({ username, password, email }).subscribe({
        next: res => {
          this.successMessage = 'Signup successful. Please log in.';
          this.showSuccessMessage = true;
          this.toggleMode();
        },
        error: err => this.showError(err)
      });
    } else {
      this.authService.login({ username, password }).subscribe({
        next: res => {
          localStorage.setItem('token', res.access_token);
          localStorage.setItem('user', JSON.stringify(res.user));
          this.successMessage = 'Login successful!';
          this.showSuccessMessage = true;
          this.router.navigate(['/dashboard']);
        },
        error: err => this.showError(err)
      });
    }
  }

  showError(err: any) {
    this.errorMessage = err?.error?.message || 'Something went wrong';
    this.showErrorMessage = true;
  }

  onForgotPassword() {
    const username = this.authForm.get('username')?.value;
    if (!username) {
      this.errorMessage = 'Please enter your username to reset password.';
      this.showErrorMessage = true;
      return;
    }

    console.log(`Forgot password requested for ${username}`);
    alert('OTP request for password reset triggered (mock).');
  }
}
