import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MaincComponent } from './mainc.component';

describe('MaincComponent', () => {
  let component: MaincComponent;
  let fixture: ComponentFixture<MaincComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MaincComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MaincComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
