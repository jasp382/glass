import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LeftcontrolComponent } from './leftcontrol.component';

describe('LeftcontrolComponent', () => {
  let component: LeftcontrolComponent;
  let fixture: ComponentFixture<LeftcontrolComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LeftcontrolComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LeftcontrolComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
