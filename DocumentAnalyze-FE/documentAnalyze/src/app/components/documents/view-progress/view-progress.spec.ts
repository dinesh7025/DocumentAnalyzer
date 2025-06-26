import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewProgress } from './view-progress';

describe('ViewProgress', () => {
  let component: ViewProgress;
  let fixture: ComponentFixture<ViewProgress>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewProgress]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ViewProgress);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
