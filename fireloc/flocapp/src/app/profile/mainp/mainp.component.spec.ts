import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MainpComponent } from './mainp.component';

describe('MainpComponent', () => {
  let component: MainpComponent;
  let fixture: ComponentFixture<MainpComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MainpComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MainpComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
