import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { WgeComponent } from './wge.component';

describe('WgeComponent', () => {
  let component: WgeComponent;
  let fixture: ComponentFixture<WgeComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ WgeComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(WgeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
