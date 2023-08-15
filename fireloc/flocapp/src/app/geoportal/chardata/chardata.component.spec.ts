import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChardataComponent } from './chardata.component';

describe('ChardataComponent', () => {
  let component: ChardataComponent;
  let fixture: ComponentFixture<ChardataComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChardataComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChardataComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
