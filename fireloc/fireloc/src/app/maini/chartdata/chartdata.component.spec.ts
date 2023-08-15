import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChartdataComponent } from './chartdata.component';

describe('TS34 ChartdataComponent', () => {
  let component: ChartdataComponent;
  let fixture: ComponentFixture<ChartdataComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ChartdataComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(ChartdataComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T34.1 should create', () => { expect(component).toBeTruthy(); });
});
