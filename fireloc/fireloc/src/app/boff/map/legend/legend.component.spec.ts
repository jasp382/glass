import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LegendComponent } from './legend.component';

describe('TS19 Backoffice LegendComponent', () => {
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

  it('T19.1 should create', () => { expect(component).toBeTruthy(); });
});
