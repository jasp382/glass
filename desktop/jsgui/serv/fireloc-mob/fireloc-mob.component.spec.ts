import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FirelocMobComponent } from './fireloc-mob.component';

describe('FirelocMobComponent', () => {
  let component: FirelocMobComponent;
  let fixture: ComponentFixture<FirelocMobComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FirelocMobComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FirelocMobComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
