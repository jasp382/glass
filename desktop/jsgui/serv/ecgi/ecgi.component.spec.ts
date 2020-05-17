import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EcgiComponent } from './ecgi.component';

describe('EcgiComponent', () => {
  let component: EcgiComponent;
  let fixture: ComponentFixture<EcgiComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EcgiComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EcgiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
