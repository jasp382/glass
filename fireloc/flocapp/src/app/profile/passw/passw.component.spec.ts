import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PasswComponent } from './passw.component';

describe('PasswComponent', () => {
  let component: PasswComponent;
  let fixture: ComponentFixture<PasswComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PasswComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PasswComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
