import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LayersbarComponent } from './layersbar.component';

describe('LayersbarComponent', () => {
  let component: LayersbarComponent;
  let fixture: ComponentFixture<LayersbarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LayersbarComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LayersbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
