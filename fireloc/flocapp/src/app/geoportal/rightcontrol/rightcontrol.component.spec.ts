import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RightcontrolComponent } from './rightcontrol.component';

describe('RightcontrolComponent', () => {
  let component: RightcontrolComponent;
  let fixture: ComponentFixture<RightcontrolComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RightcontrolComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RightcontrolComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
