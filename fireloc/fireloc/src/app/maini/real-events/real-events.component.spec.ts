// Testing
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';

// Module
import { routes } from 'src/app/app-routing.module';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { FeatModule } from 'src/app/feat/feat.module';

// Redux
import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';
import { RealEventActions } from 'src/app/redux/actions/realEventActions';
import { INITIAL_STATE_LANG } from 'src/app/redux/reducers/langReducer';
import { selectLanguage, selectRealEvent } from 'src/app/redux/selectors';
import { RealEvent } from 'src/app/interfaces/realEvents';
import { INITIAL_STATE_REAL_EVENT } from 'src/app/redux/reducers/realEventReducer';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';

import { RealEventsComponent } from './real-events.component';
import { of, Subscription, throwError } from 'rxjs';

describe('TS42 RealEventsComponent', () => {
  let component: RealEventsComponent;
  let fixture: ComponentFixture<RealEventsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [RealEventsComponent],
      imports: [
        HttpClientTestingModule,
        FontAwesomeModule,
        NgReduxTestingModule,
        RouterTestingModule.withRoutes(routes),
        FeatModule,
        TranslateModule.forRoot({
          loader: {
            provide: TranslateLoader,
            useFactory: httpTranslateLoader,
            deps: [HttpClient]
          }
        }),
      ],
      providers: [ContributionActions, EventActions, RealEventActions]
    }).compileComponents();

    // reset redux
    MockNgRedux.reset();

    fixture = TestBed.createComponent(RealEventsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T42.1 should create', () => { expect(component).toBeTruthy(); });

  describe('TS42.1 Redux subscriptions', () => {
    it('T42.1.1 should subscribe to redux for real events (no real events)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');

      // select date range state and initialize
      const eventStub = MockNgRedux.getSelectorStub(selectRealEvent);
      eventStub.next(INITIAL_STATE_REAL_EVENT);
      eventStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.reduxEvents$.subscribe(
        (actualInfo: any) => {
          // info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_REAL_EVENT);
          expect(component.fullEvents).toEqual(INITIAL_STATE_REAL_EVENT.events);
          expect(component.noEvents).toBeTrue();
          expect(component.loadingEvents).toBeFalse();
        }
      );
    });

    it('T42.1.2 should subscribe to redux for real events (real events from redux)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let event: RealEvent = {
        startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        cause: '', name: '', place: '', type: null, codncco: '', codsgif: ''
      };

      // select date range state and initialize
      const eventStub = MockNgRedux.getSelectorStub(selectRealEvent);
      eventStub.next({ events: [event] });
      eventStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.reduxEvents$.subscribe(
        (actualInfo: any) => {
          // info received should be as expected        
          expect(component.fullEvents.length).toEqual(1);
          expect(component.noEvents).toBeFalse();
          expect(component.loadingEvents).toBeFalse();
        }
      );
    });

    it('T42.1.3 should subscribe to redux for app language updates', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');

      // select lang state and initialize
      const langStub = MockNgRedux.getSelectorStub(selectLanguage);
      langStub.next(INITIAL_STATE_LANG.language);
      langStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.langRedux$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_LANG.language);
          expect(component.language).toEqual(INITIAL_STATE_LANG.language);
        }
      );
    });

    it('T42.1.4 should unsubscribe from redux selectors when component is destroyed', () => {
      // spies
      let eventSpy = spyOn(component.eventsSub, 'unsubscribe');
      let langSpy = spyOn(component.langSub, 'unsubscribe');

      component.ngOnDestroy();

      // expectations
      expect(eventSpy).toHaveBeenCalled();
      expect(langSpy).toHaveBeenCalled();
    });

    it('T42.1.5 should not unsubscribe from redux selectors if subscriptions were not created', () => {
      // spies and setup
      let eventSpy = spyOn(component.eventsSub, 'unsubscribe');
      let langSpy = spyOn(component.langSub, 'unsubscribe');

      let sub!: Subscription;
      component.eventsSub = sub;
      component.langSub = sub;
      fixture.detectChanges();

      component.ngOnDestroy();

      // expectations
      expect(eventSpy).not.toHaveBeenCalled();
      expect(langSpy).not.toHaveBeenCalled();
    });
  });

  describe('TS42.2 Get real events', () => {
    it('T42.2.1 should get events with access token if user is logged in', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getRealEventsNoToken');
      let tokenSpy = spyOn(component, 'getRealEventsToken');
      component.isLoggedIn = true;
      fixture.detectChanges();

      component.ngOnInit();

      expect(component.isLoggedIn).toBeTrue();
      expect(noTokenSpy).not.toHaveBeenCalled();
      expect(tokenSpy).toHaveBeenCalled();
    });

    it('T42.2.2 should not get events with access token if user is not logged in', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getRealEventsNoToken');
      let tokenSpy = spyOn(component, 'getRealEventsToken');
      component.isLoggedIn = false;
      fixture.detectChanges();

      component.ngOnInit();

      expect(component.isLoggedIn).toBeFalse();
      expect(noTokenSpy).toHaveBeenCalled();
      expect(tokenSpy).not.toHaveBeenCalled();
    });

    it('T42.2.3 should get events with access token from API (portuguese app language)', () => {
      // spies
      let tokenSpy = spyOn(component, 'getRealEventsToken').and.callThrough();
      let serviceSpy = spyOn(component['realEventServ'], 'getRealEventsToken').and.returnValue(of({
        data: [{
          start: '2022-03-23 19:26:33+00', end: '2022-03-23 19:26:33+00',
          name: 'name', place: 'place', causa: 'cause', tipo: 'type', codncco: 'codn', codsgif: 'cods'
        }]
      }));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['realEventActions'], 'addRealEvents');
      component.isLoggedIn = true;
      component.language = 'pt';
      fixture.detectChanges();

      component.getRealEventsToken();

      expect(tokenSpy).toHaveBeenCalled();
      expect(serviceSpy).toHaveBeenCalled();
      expect(infoSpy).toHaveBeenCalled();
      expect(actionSpy).toHaveBeenCalled();
    });

    it('T42.2.4 should get events with access token from API (english app language)', () => {
      // spies
      let tokenSpy = spyOn(component, 'getRealEventsToken').and.callThrough();
      let serviceSpy = spyOn(component['realEventServ'], 'getRealEventsToken').and.returnValue(of({
        data: [{
          start: '2022-03-23 19:26:33+00', end: '2022-03-23 19:26:33+00',
          name: 'name', place: 'place', causa: 'cause', tipo: 'type', codncco: 'codn', codsgif: 'cods'
        }]
      }));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['realEventActions'], 'addRealEvents');
      component.isLoggedIn = true;
      component.language = 'en';
      fixture.detectChanges();

      component.getRealEventsToken();

      expect(tokenSpy).toHaveBeenCalled();
      expect(serviceSpy).toHaveBeenCalled();
      expect(infoSpy).toHaveBeenCalled();
      expect(actionSpy).toHaveBeenCalled();
    });

    it('T42.2.5 should handle error from getting events with access token from API', () => {
      // spies
      let tokenSpy = spyOn(component, 'getRealEventsToken').and.callThrough();
      let serviceSpy = spyOn(component['realEventServ'], 'getRealEventsToken').and.returnValue(throwError(() => new Error()));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['realEventActions'], 'addRealEvents');
      component.isLoggedIn = true;
      fixture.detectChanges();

      component.getRealEventsToken();

      expect(tokenSpy).toHaveBeenCalled();
      expect(serviceSpy).toHaveBeenCalled();
      expect(infoSpy).not.toHaveBeenCalled();
      expect(actionSpy).not.toHaveBeenCalled();
    });

    it('T42.2.6 should not get events with access token from API if there are events stored already', () => {
      // spies
      let tokenSpy = spyOn(component, 'getRealEventsToken').and.callThrough();
      let serviceSpy = spyOn(component['realEventServ'], 'getRealEventsToken').and.returnValue(throwError(() => new Error()));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['realEventActions'], 'addRealEvents');

      let event: RealEvent = {
        startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 }, endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        cause: '', name: '', place: '', type: '', codncco: '', codsgif: ''
      };
      component.fullEvents = [event];
      component.isLoggedIn = true;
      fixture.detectChanges();

      component.getRealEventsToken();

      expect(tokenSpy).toHaveBeenCalled();
      expect(serviceSpy).not.toHaveBeenCalled();
      expect(infoSpy).not.toHaveBeenCalled();
      expect(actionSpy).not.toHaveBeenCalled();
    });

    it('T42.2.7 should get events without access token from API (portuguese app language)', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getRealEventsNoToken').and.callThrough();
      let serviceSpy = spyOn(component['realEventServ'], 'getRealEventsNoToken').and.returnValue(of({
        data: [{
          start: '2022-03-23 19:26:33+00', end: '2022-03-23 19:26:33+00',
          name: null, place: null, causa: 'cause', tipo: 'type', codncco: 'codn', codsgif: 'cods'
        }]
      }));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['realEventActions'], 'addRealEvents');
      component.isLoggedIn = false;
      component.language = 'pt'
      fixture.detectChanges();

      component.getRealEventsNoToken();

      expect(noTokenSpy).toHaveBeenCalled();
      expect(serviceSpy).toHaveBeenCalled();
      expect(infoSpy).toHaveBeenCalled();
      expect(actionSpy).toHaveBeenCalled();
    });

    it('T42.2.8 should get events without access token from API (english app language)', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getRealEventsNoToken').and.callThrough();
      let serviceSpy = spyOn(component['realEventServ'], 'getRealEventsNoToken').and.returnValue(of({
        data: [{
          start: '2022-03-23 19:26:33+00', end: '2022-03-23 19:26:33+00',
          name: null, place: null, causa: 'cause', tipo: 'type', codncco: 'codn', codsgif: 'cods'
        }]
      }));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['realEventActions'], 'addRealEvents');
      component.isLoggedIn = false;
      component.language = 'en'
      fixture.detectChanges();

      component.getRealEventsNoToken();

      expect(noTokenSpy).toHaveBeenCalled();
      expect(serviceSpy).toHaveBeenCalled();
      expect(infoSpy).toHaveBeenCalled();
      expect(actionSpy).toHaveBeenCalled();
    });

    it('T42.2.9 should handle error from getting events without access token from API', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getRealEventsNoToken').and.callThrough();
      let serviceSpy = spyOn(component['realEventServ'], 'getRealEventsNoToken').and.returnValue(throwError(() => new Error()));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['realEventActions'], 'addRealEvents');
      component.isLoggedIn = false;
      fixture.detectChanges();

      component.getRealEventsNoToken();

      expect(noTokenSpy).toHaveBeenCalled();
      expect(serviceSpy).toHaveBeenCalled();
      expect(infoSpy).not.toHaveBeenCalled();
      expect(actionSpy).not.toHaveBeenCalled();
    });

    it('T42.2.10 should not get events without access token from API if there are events stored already', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getRealEventsNoToken').and.callThrough();
      let serviceSpy = spyOn(component['realEventServ'], 'getRealEventsNoToken');
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['realEventActions'], 'addRealEvents');

      let event: RealEvent = {
        startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 }, endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        cause: '', name: '', place: '', type: '', codncco: '', codsgif: ''
      };
      component.fullEvents = [event];
      component.isLoggedIn = false;
      fixture.detectChanges();

      component.getRealEventsNoToken();

      expect(noTokenSpy).toHaveBeenCalled();
      expect(serviceSpy).not.toHaveBeenCalled();
      expect(infoSpy).not.toHaveBeenCalled();
      expect(actionSpy).not.toHaveBeenCalled();
    });
  });

  describe('TS42.3 See real event', () => {
    it('T42.3.1 should open real event', () => {
      // spies and setup
      let openSpy = spyOn(component, 'openEvent').and.callThrough();
      let event: RealEvent = {
        startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 }, endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        cause: '', name: '', place: '', type: '', codncco: '', codsgif: ''
      };
      let index = 1;

      component.openEvent(event, index);

      // expectations
      expect(openSpy).toHaveBeenCalledOnceWith(event, index);
      expect(component.isEventOpen).toBeTrue();
      expect(component.eventIndex).toBe(index);
    });

    it('T42.3.2 should change event information displayed', () => {
      let infoSpy = spyOn(component, 'seeEventInformation').and.callThrough();
      component.seeEventInformation(1);
      expect(infoSpy).toHaveBeenCalled();
      expect(component.eventInformationToggle).toBe(1);
    });

    it('T42.3.3 should close real event', () => {
      // spies and setup
      let closeSpy = spyOn(component, 'closeEvent').and.callThrough();
      component.closeEvent();

      // expectations
      expect(closeSpy).toHaveBeenCalledOnceWith();
      expect(component.isEventOpen).toBeFalse();
      expect(component.eventIndex).toBe(-1);
    });
  });

});
