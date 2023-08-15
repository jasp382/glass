import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LayersmapComponent } from './layersmap.component';

describe('LayersmapComponent', () => {
  let component: LayersmapComponent;
  let fixture: ComponentFixture<LayersmapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LayersmapComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LayersmapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
