import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeomsComponent } from './geoms.component';

describe('GeomsComponent', () => {
  let component: GeomsComponent;
  let fixture: ComponentFixture<GeomsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GeomsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeomsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
