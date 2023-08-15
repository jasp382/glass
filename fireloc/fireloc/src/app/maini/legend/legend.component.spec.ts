import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LegendComponent } from './legend.component';

describe('TS39 LegendComponent', () => {
  let component: LegendComponent;
  let fixture: ComponentFixture<LegendComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [LegendComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(LegendComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T39.1 should create', () => { expect(component).toBeTruthy(); });
});
