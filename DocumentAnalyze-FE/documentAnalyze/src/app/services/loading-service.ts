import { Injectable } from '@angular/core';
import { BehaviorSubject, timer } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LoadingService {

  private loadingSubject = new BehaviorSubject<boolean>(false);
  loading$ = this.loadingSubject.asObservable();

  private spinnerStartTime: number | null = null;

  show(): void {
    this.spinnerStartTime = Date.now();
    this.loadingSubject.next(true);
  }

  hide(): void {
    const now = Date.now();
    const minDuration = 2000; // 2 seconds
    const elapsed = this.spinnerStartTime ? now - this.spinnerStartTime : minDuration;
    const delay = Math.max(minDuration - elapsed, 0);

    setTimeout(() => {
      this.loadingSubject.next(false);
      this.spinnerStartTime = null;
    }, delay);
  }
}
