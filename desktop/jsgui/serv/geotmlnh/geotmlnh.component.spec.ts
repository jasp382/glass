import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GeotmlnhComponent } from './geotmlnh.component';

describe('GeotmlnhComponent', () => {
  let component: GeotmlnhComponent;
  let fixture: ComponentFixture<GeotmlnhComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GeotmlnhComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GeotmlnhComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
