import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FlocsComponent } from './flocs.component';

describe('FlocsComponent', () => {
  let component: FlocsComponent;
  let fixture: ComponentFixture<FlocsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FlocsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FlocsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
