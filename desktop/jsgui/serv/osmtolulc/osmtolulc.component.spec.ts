import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OsmtolulcComponent } from './osmtolulc.component';

describe('OsmtolulcComponent', () => {
  let component: OsmtolulcComponent;
  let fixture: ComponentFixture<OsmtolulcComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OsmtolulcComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OsmtolulcComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
