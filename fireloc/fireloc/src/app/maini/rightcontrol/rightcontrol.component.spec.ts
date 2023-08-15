import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Component
import { RightcontrolComponent } from './rightcontrol.component';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';
import { HttpClientTestingModule } from '@angular/common/http/testing';

describe('TS43 RightcontrolComponent', () => {
  let component: RightcontrolComponent;
  let fixture: ComponentFixture<RightcontrolComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [RightcontrolComponent],
      imports: [
        NgbModule,
        HttpClientTestingModule,
        TranslateModule.forRoot({
          loader: {
            provide: TranslateLoader,
            useFactory: httpTranslateLoader,
            deps: [HttpClient]
          }
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(RightcontrolComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T43.1 should create', () => {
    expect(component).toBeTruthy();
  });

  it('T43.2 should open tab 1', () => {
    let toggleSpy = spyOn(component, 'toggleTab').and.callThrough();
    component.toggleTab(1);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(1);
    expect(component.tab1Active).toBeTrue();
    expect(component.tab2Active).toBeFalse();
    expect(component.tab3Active).toBeFalse();
    expect(component.tab4Active).toBeFalse();
  });

  it('T43.3 should close tab 1', () => {
    let toggleSpy = spyOn(component, 'toggleTab').and.callThrough();
    component.tab1Active = true;
    fixture.detectChanges();
    component.toggleTab(1);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(1);
    expect(component.activeTab).toBe(0);
    expect(component.tab1Active).toBeFalse();
    expect(component.tab2Active).toBeFalse();
    expect(component.tab3Active).toBeFalse();
    expect(component.tab4Active).toBeFalse();
  });

  it('T43.4 should open tab 2', () => {
    let toggleSpy = spyOn(component, 'toggleTab').and.callThrough();
    component.toggleTab(2);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(2);
    expect(component.tab2Active).toBeTrue();
    expect(component.tab1Active).toBeFalse();
    expect(component.tab3Active).toBeFalse();
    expect(component.tab4Active).toBeFalse();
  });

  it('T43.5 should close tab 2', () => {
    let toggleSpy = spyOn(component, 'toggleTab').and.callThrough();
    component.tab2Active = true;
    fixture.detectChanges();
    component.toggleTab(2);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(2);
    expect(component.activeTab).toBe(0);
    expect(component.tab1Active).toBeFalse();
    expect(component.tab2Active).toBeFalse();
    expect(component.tab3Active).toBeFalse();
    expect(component.tab4Active).toBeFalse();
  });

  it('T43.6 should open tab 3', () => {
    let toggleSpy = spyOn(component, 'toggleTab').and.callThrough();
    component.toggleTab(3);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(3);
    expect(component.tab3Active).toBeTrue();
    expect(component.tab1Active).toBeFalse();
    expect(component.tab2Active).toBeFalse();
    expect(component.tab4Active).toBeFalse();
  });

  it('T43.7 should close tab 3', () => {
    let toggleSpy = spyOn(component, 'toggleTab').and.callThrough();
    component.tab3Active = true;
    fixture.detectChanges();
    component.toggleTab(3);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(3);
    expect(component.activeTab).toBe(0);
    expect(component.tab1Active).toBeFalse();
    expect(component.tab2Active).toBeFalse();
    expect(component.tab3Active).toBeFalse();
    expect(component.tab4Active).toBeFalse();
  });

  it('T43.8 should open tab 4', () => {
    let toggleSpy = spyOn(component, 'toggleTab').and.callThrough();
    component.toggleTab(4);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(4);
    expect(component.tab4Active).toBeTrue();
    expect(component.tab1Active).toBeFalse();
    expect(component.tab2Active).toBeFalse();
    expect(component.tab3Active).toBeFalse();
  });

  it('T43.9 should close tab 4', () => {
    let toggleSpy = spyOn(component, 'toggleTab').and.callThrough();
    component.tab4Active = true;
    fixture.detectChanges();
    component.toggleTab(4);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(4);
    expect(component.activeTab).toBe(0);
    expect(component.tab1Active).toBeFalse();
    expect(component.tab2Active).toBeFalse();
    expect(component.tab3Active).toBeFalse();
    expect(component.tab4Active).toBeFalse();
  });

  it('T43.10 should receive contribution toggle', () => {
    let toggleSpy = spyOn(component, 'receiveContribToggle').and.callThrough();
    let emitSpy = spyOn(component['allContribsEmitter'], 'emit');

    component.receiveContribToggle(true);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(true);
    expect(emitSpy).toHaveBeenCalledOnceWith(true);
    expect(component.allContribsSelected).toBeTrue();
  });
});
