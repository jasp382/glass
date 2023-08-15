import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VetorialComponent } from './vetorial.component';

describe('VetorialComponent', () => {
  let component: VetorialComponent;
  let fixture: ComponentFixture<VetorialComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VetorialComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VetorialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
