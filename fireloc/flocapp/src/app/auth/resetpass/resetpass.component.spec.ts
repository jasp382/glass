import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResetpassComponent } from './resetpass.component';

describe('ResetpassComponent', () => {
  let component: ResetpassComponent;
  let fixture: ComponentFixture<ResetpassComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ResetpassComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ResetpassComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
