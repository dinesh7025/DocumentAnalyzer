import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RouteDialog } from './route-dialog';

describe('RouteDialog', () => {
  let component: RouteDialog;
  let fixture: ComponentFixture<RouteDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouteDialog]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RouteDialog);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
