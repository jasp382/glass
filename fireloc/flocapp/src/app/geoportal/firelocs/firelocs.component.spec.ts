import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FirelocsComponent } from './firelocs.component';

describe('FirelocsComponent', () => {
  let component: FirelocsComponent;
  let fixture: ComponentFixture<FirelocsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FirelocsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FirelocsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
