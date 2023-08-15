import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContribComponent } from './contrib.component';

describe('ContribComponent', () => {
  let component: ContribComponent;
  let fixture: ComponentFixture<ContribComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ContribComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContribComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
