// Testing
import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { By } from '@angular/platform-browser';

// Modules
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { FeatModule } from 'src/app/feat/feat.module';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { of, Subscription, throwError } from 'rxjs';

// Interfaces and Constants
import { Event, ServiceLayer } from 'src/app/interfaces/events';
import { routes } from 'src/app/app-routing.module';

// Redux
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';
import { INITIAL_STATE_DATERANGE } from 'src/app/redux/reducers/dateRangeReducer';
import { INITIAL_STATE_EVENT } from 'src/app/redux/reducers/eventReducer';
import { selectDateRange, selectEvent } from 'src/app/redux/selectors';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';

import { EventsComponent } from './events.component';

describe('TS36 EventsComponent', () => {
  let component: EventsComponent;
  let fixture: ComponentFixture<EventsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [EventsComponent],
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
      providers: [NgbActiveModal, ContributionActions, EventActions,]
    }).compileComponents();

    // reset redux
    MockNgRedux.reset();

    fixture = TestBed.createComponent(EventsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T36.1 should create', () => { expect(component).toBeTruthy(); });

  describe('TS36.1 Redux subscriptions', () => {
    it('T36.1.1 should subscribe to redux for events (no events)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');

      // select date range state and initialize
      const eventStub = MockNgRedux.getSelectorStub(selectEvent);
      eventStub.next(INITIAL_STATE_EVENT);
      eventStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.reduxEvents$.subscribe(
        (actualInfo: any) => {
          // info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_EVENT);
          expect(component.fullEvents).toEqual(INITIAL_STATE_EVENT.events);
          expect(component.noEvents).toBeTrue();
          expect(component.loadingEvents).toBeFalse();
        }
      );
    });

    it('T36.1.2 should subscribe to redux for date range (no events)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let filterEventsSpy = spyOn(component, 'filterEventsByDate');

      // select date range state and initialize
      const rangeStub = MockNgRedux.getSelectorStub(selectDateRange);
      rangeStub.next(INITIAL_STATE_DATERANGE);
      rangeStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.dateRange$.subscribe(
        (actualInfo: any) => {
          // info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_DATERANGE);
          expect(component.minDate).toEqual(INITIAL_STATE_DATERANGE.minDate);
          expect(component.maxDate).toEqual(INITIAL_STATE_DATERANGE.maxDate);
          expect(filterEventsSpy).toHaveBeenCalled();
          expect(component.loadingEvents).toBeFalse();
        }
      );
    });

    it('T36.1.3 should subscribe to redux for events (events from redux)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let event: Event = {
        id: 1, startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 }, endTime: null,
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: [], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      };

      // select date range state and initialize
      const eventStub = MockNgRedux.getSelectorStub(selectEvent);
      eventStub.next({ events: [event], serviceLayers: [] });
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

    it('T36.1.4 should subscribe to redux for date range (has events)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let filterEventsSpy = spyOn(component, 'filterEventsByDate');

      let event: Event = {
        id: 1, startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 }, endTime: null,
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: [], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      };
      component.fullEvents = [event];
      fixture.detectChanges();

      // select date range state and initialize
      const rangeStub = MockNgRedux.getSelectorStub(selectDateRange);
      rangeStub.next(INITIAL_STATE_DATERANGE);
      rangeStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.dateRange$.subscribe(
        (actualInfo: any) => {
          // info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_DATERANGE);
          expect(component.minDate).toEqual(INITIAL_STATE_DATERANGE.minDate);
          expect(component.maxDate).toEqual(INITIAL_STATE_DATERANGE.maxDate);
          expect(filterEventsSpy).toHaveBeenCalled();
          expect(component.noEvents).toBeFalse();
          expect(component.loadingEvents).toBeFalse();
        }
      );
    });

    it('T36.1.5 should unsubscribe from redux selectors when component is destroyed', () => {
      // spies
      let eventSpy = spyOn(component.eventsSub, 'unsubscribe');
      let dateSpy = spyOn(component.dateRangeSub, 'unsubscribe');

      component.ngOnDestroy();

      // expectations
      expect(eventSpy).toHaveBeenCalled();
      expect(dateSpy).toHaveBeenCalled();
    });

    it('T36.1.6 should not unsubscribe from redux selectors if subscriptions were not created', () => {
      // spies and setup
      let eventSpy = spyOn(component.eventsSub, 'unsubscribe');
      let dateSpy = spyOn(component.dateRangeSub, 'unsubscribe');

      let sub!: Subscription;
      component.eventsSub = sub;
      component.dateRangeSub = sub;
      fixture.detectChanges();

      component.ngOnDestroy();

      // expectations
      expect(eventSpy).not.toHaveBeenCalled();
      expect(dateSpy).not.toHaveBeenCalled();
    });
  });

  describe('TS36.2 Get events', () => {
    it('T36.2.1 should get events with access token if user is logged in', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getAllEventsNoToken');
      let tokenSpy = spyOn(component, 'getAllEventsToken');
      component.isLoggedIn = true;
      fixture.detectChanges();

      component.ngOnInit();

      expect(component.isLoggedIn).toBeTrue();
      expect(noTokenSpy).not.toHaveBeenCalled();
      expect(tokenSpy).toHaveBeenCalled();
    });

    it('T36.2.2 should not get events with access token if user is not logged in', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getAllEventsNoToken');
      let tokenSpy = spyOn(component, 'getAllEventsToken');
      component.isLoggedIn = false;
      fixture.detectChanges();

      component.ngOnInit();

      expect(component.isLoggedIn).toBeFalse();
      expect(noTokenSpy).toHaveBeenCalled();
      expect(tokenSpy).not.toHaveBeenCalled();
    });

    it('T36.2.3 should get events with access token from API', () => {
      // spies
      let tokenSpy = spyOn(component, 'getAllEventsToken').and.callThrough();
      let serviceSpy = spyOn(component['eventServ'], 'getEventsToken').and.returnValue(of({
        data: [{
          startime: '2022-03-23T19:26:33Z', endtime: '2022-03-23T19:26:33Z',
          contribstart: '2022-03-23T19:26:33Z', contribend: '2022-03-23T19:26:33Z',
          id: 1, nearplace: 1,
          floclyr: [
            { id: 1, glyr: '', slug: '', store: '', style: '', work: '', design: '' }
          ],
          flocctb: ['', ''],
          place: { fid: 1, fregid: 1, lugid: 1, geom: '', lugname: '' },
          attr: [{ id: 1, slug: '', name: '', value: '' }]
        }]
      }));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['eventActions'], 'addEvents');
      component.isLoggedIn = true;
      fixture.detectChanges();

      component.getAllEventsToken();

      expect(tokenSpy).toHaveBeenCalled();
      expect(serviceSpy).toHaveBeenCalled();
      expect(infoSpy).toHaveBeenCalled();
      expect(actionSpy).toHaveBeenCalled();
      expect(component.loadingEvents).toBeFalse();
    });

    it('T36.2.4 should handle error from getting events with access token from API', () => {
      // spies
      let tokenSpy = spyOn(component, 'getAllEventsToken').and.callThrough();
      let serviceSpy = spyOn(component['eventServ'], 'getEventsToken').and.returnValue(throwError(() => new Error()));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['eventActions'], 'addEvents');
      component.isLoggedIn = true;
      fixture.detectChanges();

      component.getAllEventsToken();

      expect(tokenSpy).toHaveBeenCalled();
      expect(serviceSpy).toHaveBeenCalled();
      expect(infoSpy).not.toHaveBeenCalled();
      expect(actionSpy).not.toHaveBeenCalled();
    });

    it('T36.2.5 should not get events with access token from API if there are events stored already', () => {
      // spies
      let tokenSpy = spyOn(component, 'getAllEventsToken').and.callThrough();
      let serviceSpy = spyOn(component['eventServ'], 'getEventsToken').and.returnValue(throwError(() => new Error()));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['eventActions'], 'addEvents');

      let event: Event = {
        id: 1, startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 }, endTime: null,
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: [], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      };
      component.fullEvents = [event];
      component.isLoggedIn = true;
      fixture.detectChanges();

      component.getAllEventsToken();

      expect(tokenSpy).toHaveBeenCalled();
      expect(serviceSpy).not.toHaveBeenCalled();
      expect(infoSpy).not.toHaveBeenCalled();
      expect(actionSpy).not.toHaveBeenCalled();
    });

    it('T36.2.6 should get events without access token from API', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getAllEventsNoToken').and.callThrough();
      let serviceSpy = spyOn(component['eventServ'], 'getEventsNoToken').and.returnValue(of({
        data: [{
          startime: '2022-03-23T19:26:33Z', endtime: null,
          contribstart: '2022-03-23T19:26:33Z', contribend: '2022-03-23T19:26:33Z',
          id: 1, nearplace: 1,
          floclyr: [
            { id: 1, glyr: '', slug: '', store: '', style: '', work: '', design: '' }
          ],
          flocctb: ['', ''],
          place: { fid: 1, fregid: 1, lugid: 1, geom: '', lugname: '' },
          attr: [{ id: 1, slug: '', name: '', value: '' }]
        }, {
          startime: '2022-03-23T19:26:33Z', endtime: null,
          contribstart: '2022-03-23T19:26:33Z', contribend: '2022-03-23T19:26:33Z',
          id: 1, nearplace: 1,
          floclyr: [
            { id: 1, glyr: '', slug: '', store: '', style: '', work: '', design: '' }
          ],
          flocctb: ['', ''],
          place: { fid: 1, fregid: 1, lugid: 1, geom: '', lugname: '' },
          attr: [{ id: 1, slug: '', name: '', value: '' }]
        }]
      }));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['eventActions'], 'addEvents');
      component.isLoggedIn = false;
      fixture.detectChanges();

      component.getAllEventsNoToken();

      expect(noTokenSpy).toHaveBeenCalled();
      expect(serviceSpy).toHaveBeenCalled();
      expect(infoSpy).toHaveBeenCalled();
      expect(actionSpy).toHaveBeenCalled();
      expect(component.loadingEvents).toBeFalse();
    });

    it('T36.2.7 should handle error from getting events without access token from API', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getAllEventsNoToken').and.callThrough();
      let serviceSpy = spyOn(component['eventServ'], 'getEventsNoToken').and.returnValue(throwError(() => new Error()));
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['eventActions'], 'addEvents');
      component.isLoggedIn = false;
      fixture.detectChanges();

      component.getAllEventsNoToken();

      expect(noTokenSpy).toHaveBeenCalled();
      expect(serviceSpy).toHaveBeenCalled();
      expect(infoSpy).not.toHaveBeenCalled();
      expect(actionSpy).not.toHaveBeenCalled();
    });

    it('T36.2.8 should not get events without access token from API if there are events stored already', () => {
      // spies
      let noTokenSpy = spyOn(component, 'getAllEventsNoToken').and.callThrough();
      let serviceSpy = spyOn(component['eventServ'], 'getEventsToken');
      let infoSpy = spyOn(component, 'getEventInformation').and.callThrough();
      let actionSpy = spyOn(component['eventActions'], 'addEvents');

      let event: Event = {
        id: 1, startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 }, endTime: null,
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: [], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      };
      component.fullEvents = [event];
      component.isLoggedIn = false;
      fixture.detectChanges();

      component.getAllEventsNoToken();

      expect(noTokenSpy).toHaveBeenCalled();
      expect(serviceSpy).not.toHaveBeenCalled();
      expect(infoSpy).not.toHaveBeenCalled();
      expect(actionSpy).not.toHaveBeenCalled();
    });
  });

  describe('TS36.3 Filter events by date', () => {
    // date filter
    it('T36.3.1 should filter events with date range', () => {
      let filterSpy = spyOn(component, 'filterEventsByDate').and.callThrough();
      let events: Event[] = [{
        id: 1, startTime: { year: 2022, month: 2, day: 10, hour: 1, minute: 1 },
        endTime: { year: 2022, month: 3, day: 10, hour: 1, minute: 1 },
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: [], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      }];
      component.minDate = new Date(2022, 1, 1);
      component.maxDate = new Date(2022, 12, 31);
      fixture.detectChanges();

      component.filterEventsByDate(events);

      // expectations
      expect(filterSpy).toHaveBeenCalledOnceWith(events);
      expect(component.filteredEvents).toEqual(events);
    });

    it('T36.3.2 should add event to filtered if date types are unexpected', () => {
      let filterSpy = spyOn(component, 'filterEventsByDate').and.callThrough();
      let events: Event[] = [{
        id: 1, startTime: { year: 2022, month: '', day: 10, hour: 1, minute: 1 },
        endTime: { year: 2022, month: 3, day: 10, hour: 1, minute: 1 },
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: [], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      }];
      component.minDate = new Date(2022, 1, 1);
      component.maxDate = new Date(2022, 12, 31);
      fixture.detectChanges();

      component.filterEventsByDate(events);

      // expectations
      expect(filterSpy).toHaveBeenCalledOnceWith(events);
      expect(component.filteredEvents).toEqual(events);
    });
  });

  describe('TS36.4 Filter events by location', () => {
    // location filter
    it('T36.4.1 should receive map for location filtering and set onClick method', () => {
      let receiveSpy = spyOn(component, 'receiveFilterMap').and.callThrough();
      component.showFilterMap = true;
      fixture.detectChanges();
      expect(receiveSpy).toHaveBeenCalled();
      expect(component.filterMap).not.toBeNull();
    });

    it('T36.4.2 should detect click on location filter map', fakeAsync(() => {
      let polylineSpy = spyOn(component, 'createPolyline');
      component.showFilterMap = true;
      fixture.detectChanges();

      // click on map
      let map = fixture.debugElement.query(By.css('#filter-map-geoEvents')).nativeElement;
      map.click();
      tick();

      // expectations
      expect(polylineSpy).toHaveBeenCalled();
    }));

    describe('TS36.4.1 should create visual elements in the filter map on click', () => {
      it('T36.4.1.1 should initialize line group', () => {
        let polylineSpy = spyOn(component, 'createPolyline').and.callThrough();
        let markerSpy = spyOn(component['markerServ'], 'startPolylineGroup');
        let markerAddSpy = spyOn(component['markerServ'], 'addPolylineToFilterMap');
        let coordinates = { lat: 1, long: 1 };

        component.createPolyline(coordinates);

        // expectations
        expect(polylineSpy).toHaveBeenCalledOnceWith(coordinates);
        expect(markerSpy).toHaveBeenCalled();
        expect(markerAddSpy).toHaveBeenCalled();
        expect(component.pointCounter).toBe(1);
      });

      it('T36.4.1.2 should add polygon when last point is added', () => {
        let polylineSpy = spyOn(component, 'createPolyline').and.callThrough();
        let markerAddSpy = spyOn(component['markerServ'], 'addPolylineToFilterMap');
        let markerAddPolygonSpy = spyOn(component['markerServ'], 'addPolygonToFilterMap');
        let coordinates = { lat: 1, long: 1 };

        component.pointCounter = 3;
        fixture.detectChanges();

        component.createPolyline(coordinates);

        // expectations
        expect(polylineSpy).toHaveBeenCalledOnceWith(coordinates);
        expect(markerAddSpy).toHaveBeenCalled();
        expect(markerAddPolygonSpy).toHaveBeenCalled();
        expect(component.pointCounter).toBe(4);
      });

      it('T36.4.1.3 should clear map when clicked after all points are added', () => {
        let polylineSpy = spyOn(component, 'createPolyline').and.callThrough();
        let clearSpy = spyOn(component, 'clearLocFilter');
        let coordinates = { lat: 1, long: 1 };

        component.pointCounter = 4;
        fixture.detectChanges();

        component.createPolyline(coordinates);

        // expectations
        expect(polylineSpy).toHaveBeenCalledOnceWith(coordinates);
        expect(clearSpy).toHaveBeenCalledOnceWith();
      });
    });

    it('T36.4.3 should toggle map when dropdown menu is open/closed', () => {
      let toggleSpy = spyOn(component, 'toggleFilterMap').and.callThrough();
      let fakeElemEmpty = { className: '' } as HTMLDivElement;
      let fakeElemShow = { className: 'show' } as HTMLDivElement;

      component.toggleFilterMap(fakeElemEmpty);
      expect(toggleSpy).toHaveBeenCalledWith(fakeElemEmpty);

      component.toggleFilterMap(fakeElemShow);
      expect(toggleSpy).toHaveBeenCalledWith(fakeElemShow);
      expect(component.pointCounter).toBe(0);
      expect(component.filterPoints).toEqual([]);
    });

    it('T36.4.4 should clear location filter', () => {
      let clearSpy = spyOn(component, 'clearLocFilter').and.callThrough();
      let markerSpy = spyOn(component['markerServ'], 'clearPolyGroup');

      component.clearLocFilter();

      // expectations
      expect(clearSpy).toHaveBeenCalled();
      expect(component.filterPoints).toEqual([]);
      expect(markerSpy).toHaveBeenCalled();
    });

    // TODO UPDATE AFTER SOURCE CODE UPDATES
    it('T36.4.5 should filter events by location', () => {
      let filterSpy = spyOn(component, 'filterLoc').and.callThrough();
      component.filterPoints = [
        [1, 1],
      ];
      fixture.detectChanges();

      component.filterLoc();

      // expectations
      expect(filterSpy).toHaveBeenCalled();
    });
  });

  describe('TS36.5 See event', () => {
    it('T36.5.1 should open event (with event end date)', () => {
      // spies and setup
      let openSpy = spyOn(component, 'openEvent').and.callThrough();
      let photoSpy = spyOn(component, 'getContribPhoto');
      let clearLayersSpy = spyOn(component['eventActions'], 'clearEventLayers');
      let event: Event = {
        id: 1, startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 }, endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: ['', ''], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      };
      component.fullEvents = [event];
      fixture.detectChanges();
      let index = 0;

      component.openEvent(event, index);

      // expectations
      expect(openSpy).toHaveBeenCalledOnceWith(event, index);
      expect(clearLayersSpy).toHaveBeenCalled();
      expect(component.isEventOpen).toBeTrue();
      expect(component.eventIndex).toBe(index);
      expect(component.eventID).toBe(event.id);
      expect(photoSpy).toHaveBeenCalled();
    });

    it('T36.5.2 should open event (without event end date)', () => {
      // spies and setup
      let openSpy = spyOn(component, 'openEvent').and.callThrough();
      let photoSpy = spyOn(component, 'getContribPhoto');
      let clearLayersSpy = spyOn(component['eventActions'], 'clearEventLayers');
      let event: Event = {
        id: 1, startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 }, endTime: null,
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: ['', ''], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      };
      component.fullEvents = [event];
      fixture.detectChanges();
      let index = 0;

      component.openEvent(event, index);

      // expectations
      expect(openSpy).toHaveBeenCalledOnceWith(event, index);
      expect(clearLayersSpy).toHaveBeenCalled();
      expect(component.isEventOpen).toBeTrue();
      expect(component.eventIndex).toBe(index);
      expect(component.eventID).toBe(event.id);
      expect(photoSpy).toHaveBeenCalled();
    });

    it('T36.5.3 should close event if clicked on list event while open', () => {
      // spies and setup
      let openSpy = spyOn(component, 'openEvent').and.callThrough();
      let closeSpy = spyOn(component, 'closeEvent').and.callThrough();
      let clearLayersSpy = spyOn(component['eventActions'], 'clearEventLayers');
      let event: Event = {
        id: 1, startTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 }, endTime: null,
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: ['', ''], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      };
      component.fullEvents = [event];
      let index = 0;
      component.eventID = 1;
      fixture.detectChanges();

      component.openEvent(event, index);

      // expectations
      expect(openSpy).toHaveBeenCalledOnceWith(event, index);
      expect(closeSpy).toHaveBeenCalledOnceWith();
      expect(component.eventID).toBe(-1);
      expect(component.eventIndex).toBe(-1);
      expect(component.isEventOpen).toBeFalse();
      expect(component.eventPhotos).toEqual([]);
      expect(clearLayersSpy).toHaveBeenCalled();
    });

    it('T36.5.4 should change event information displayed', () => {
      let infoSpy = spyOn(component, 'seeEventInformation').and.callThrough();
      component.seeEventInformation(1);
      expect(infoSpy).toHaveBeenCalled();
      expect(component.eventInformationToggle).toBe(1);
    });

    it('T36.5.5 should add layers in redux to show in map', () => {
      let layerSpy = spyOn(component, 'selectEventLayer').and.callThrough();
      let actionAddSpy = spyOn(component['eventActions'], 'addEventLayer');
      let actionRemoveSpy = spyOn(component['eventActions'], 'removeEventLayer');
      let ev = { target: { checked: true } };
      let layer: ServiceLayer = { id: 0, gLayer: '', slug: '', store: '', style: '', work: '', design: '' }

      component.selectEventLayer(ev, layer);
      expect(layerSpy).toHaveBeenCalled();
      expect(actionAddSpy).toHaveBeenCalled();
      expect(actionRemoveSpy).not.toHaveBeenCalled();
    });

    it('T36.5.6 should add layers in redux to show in map', () => {
      let layerSpy = spyOn(component, 'selectEventLayer').and.callThrough();
      let actionAddSpy = spyOn(component['eventActions'], 'addEventLayer');
      let actionRemoveSpy = spyOn(component['eventActions'], 'removeEventLayer');
      let ev = { target: { checked: false } };
      let layer: ServiceLayer = { id: 0, gLayer: '', slug: '', store: '', style: '', work: '', design: '' }

      component.selectEventLayer(ev, layer);
      expect(layerSpy).toHaveBeenCalled();
      expect(actionAddSpy).not.toHaveBeenCalled();
      expect(actionRemoveSpy).toHaveBeenCalled();
    });

  });

  describe('TS36.6 Get contribution photo', () => {
    it('T36.6.1 should get contribution photo from API', () => {
      let getPhotoSpy = spyOn(component, 'getContribPhoto').and.callThrough();
      let getPhotoServSpy = spyOn(component['contribServ'], 'getContributionPhoto').and.returnValue(of({ data: 'photoData' }));
      component.getContribPhoto('');

      // expectations
      expect(getPhotoSpy).toHaveBeenCalled();
      expect(getPhotoServSpy).toHaveBeenCalled();
    });

    it('T36.6.2 should handle get contribution photo error from API', () => {
      let getPhotoSpy = spyOn(component, 'getContribPhoto').and.callThrough();
      let getPhotoServSpy = spyOn(component['contribServ'], 'getContributionPhoto').and.returnValue(throwError(() => new Error()));

      component.getContribPhoto('');

      // expectations
      expect(getPhotoSpy).toHaveBeenCalledOnceWith('');
      expect(getPhotoServSpy).toHaveBeenCalledOnceWith('');
    });

    it('T36.6.3 should open contribution photo', () => {
      let modalServiceSpy = spyOn(component['modalService'], 'open').and.callThrough();
      let content: HTMLElement = fixture.debugElement.nativeElement.querySelector('#modal-container');
      component.openContribPhoto(content, '');
      expect(modalServiceSpy).toHaveBeenCalled();
    });
  });

});
