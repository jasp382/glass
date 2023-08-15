import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CtbComponent } from './ctb.component';

describe('CtbComponent', () => {
  let component: CtbComponent;
  let fixture: ComponentFixture<CtbComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CtbComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CtbComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
