import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RasterComponent } from './raster.component';

describe('RasterComponent', () => {
  let component: RasterComponent;
  let fixture: ComponentFixture<RasterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RasterComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RasterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
