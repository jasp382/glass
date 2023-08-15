import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { FormControl, FormGroup } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbDate, NgbDateStruct, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { of, throwError } from 'rxjs';
import { FeatModule } from 'src/app/feat/feat.module';
import { RealEvent } from 'src/app/interfaces/events';

import { RealEventsComponent } from './real-events.component';

describe('TS20 Backoffice RealEventsComponent', () => {
  let component: RealEventsComponent;
  let fixture: ComponentFixture<RealEventsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [RealEventsComponent],
      imports: [
        HttpClientTestingModule,
        FeatModule,
        FontAwesomeModule,
        NgbModule,
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(RealEventsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => { expect(component).toBeTruthy(); });

  it('T20.1 should update search terms', () => {
    // spies
    let searchSpy = spyOn(component, 'searchRealEvents').and.callThrough();

    component.searchRealEvents(null as unknown as string);
    component.searchRealEvents('search');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('search');
    expect(component.searchTerms).toEqual('search');
  });

  it('T20.2 should update data row count for pagination', () => {
    // setup
    let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();

    component.updateRowCount(10);

    // expectations
    expect(rowSpy).toHaveBeenCalledOnceWith(10);
    expect(component.rowCount).toBe(10);
  });

  it('T20.3 should get current page for table component', () => {
    // setup
    let pageSpy = spyOn(component, 'getPage').and.callThrough();

    component.getPage(5);

    // expectations
    expect(pageSpy).toHaveBeenCalledOnceWith(5);
    expect(component.currentPage).toBe(5);
  });

  it('T20.4 should get real events from API', () => {
    // setup
    let getEventsSpy = spyOn(component, 'getRealEvents').and.callThrough();
    let eventsAPISpy = spyOn(component['eventServ'], 'getRealEventsToken').and.returnValue(of({
      data: [
        { id: 1, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: '' },
        {
          id: 2, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: '',
          firelyr: [{ id: 1, fireid: 1, design: '', glyr: '', slug: '', store: '', style: '', work: '' }],
          freg: [{ fid: 1, code: '', name: '', munid: 1 }],
          mun: [{ fid: 1, code: '', name: '', nutiii: '' }]
        },
        {
          id: 3, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: '',
          firelyr: null, freg: null, mun: null
        },
      ]
    }));
    let eventInfoSpy = spyOn(component, 'getEventData').and.callThrough();
    let fregInfoSpy = spyOn(component, 'getFreg').and.callThrough();
    let munInfoSpy = spyOn(component, 'getMun').and.callThrough();
    let fireInfoSpy = spyOn(component, 'getFireLayers').and.callThrough();
    let updateRowSpy = spyOn(component, 'updateRowCount');

    component.getRealEvents();

    // expectations
    expect(getEventsSpy).toHaveBeenCalled();
    expect(eventsAPISpy).toHaveBeenCalled();
    expect(eventInfoSpy).toHaveBeenCalled();
    expect(fregInfoSpy).toHaveBeenCalled();
    expect(munInfoSpy).toHaveBeenCalled();
    expect(fireInfoSpy).toHaveBeenCalled();
    expect(updateRowSpy).toHaveBeenCalled();
  });

  it('T20.5 should handle error from getting real events from API', () => {
    // setup
    let getEventsSpy = spyOn(component, 'getRealEvents').and.callThrough();
    let eventsAPISpy = spyOn(component['eventServ'], 'getRealEventsToken').and.returnValue(throwError(() => new Error()));
    let eventInfoSpy = spyOn(component, 'getEventData').and.callThrough();
    let fregInfoSpy = spyOn(component, 'getFreg').and.callThrough();
    let munInfoSpy = spyOn(component, 'getMun').and.callThrough();
    let fireInfoSpy = spyOn(component, 'getFireLayers').and.callThrough();
    let updateRowSpy = spyOn(component, 'updateRowCount');

    component.getRealEvents();

    // expectations
    expect(getEventsSpy).toHaveBeenCalled();
    expect(eventsAPISpy).toHaveBeenCalled();
    expect(eventInfoSpy).not.toHaveBeenCalled();
    expect(fregInfoSpy).not.toHaveBeenCalled();
    expect(munInfoSpy).not.toHaveBeenCalled();
    expect(fireInfoSpy).not.toHaveBeenCalled();
    expect(updateRowSpy).not.toHaveBeenCalled();
  });

  describe('TS20.1 filter real events by date', () => {
    it('T20.1.1 should select start date if no dates are selected', () => {
      let dateSpy = spyOn(component, 'onDateSelection').and.callThrough();
      let fromDate: NgbDate = {
        year: 2022,
        month: 12,
        day: 15,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return false; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return true; }
      }
      let eventsAPISpy = spyOn(component['eventServ'], 'getRealEventsToken');

      component.onDateSelection(fromDate);

      expect(dateSpy).toHaveBeenCalled();
      expect(eventsAPISpy).not.toHaveBeenCalled();
      expect(component.fromDate).toEqual(fromDate);
    });

    it('T20.1.2 should renew start date if dates are selected but new date is before the set start date', () => {
      let dateSpy = spyOn(component, 'onDateSelection').and.callThrough();
      let fromDate: NgbDate = {
        year: 2022, month: 12, day: 15,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return false; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return false; }
      }
      let toDate: NgbDate = {
        year: 2022, month: 12, day: 20,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return false; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return false; }
      }
      let newDate: NgbDate = {
        year: 2022, month: 12, day: 10,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return false; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return false; }
      }
      let eventsAPISpy = spyOn(component['eventServ'], 'getRealEventsToken');
      component.fromDate = fromDate;
      component.toDate = toDate;
      fixture.detectChanges();

      component.onDateSelection(newDate);

      expect(dateSpy).toHaveBeenCalled();
      expect(eventsAPISpy).not.toHaveBeenCalled();
      expect(component.fromDate).toEqual(newDate);
      expect(component.toDate).toBeNull();
    });

    it('T20.1.3 should filter events by selected date range', () => {
      let dateSpy = spyOn(component, 'onDateSelection').and.callThrough();
      let updateRowSpy = spyOn(component, 'updateRowCount');
      let fromDate: NgbDate = {
        year: 2022, month: 12, day: 15,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return false; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return false; }
      }
      let newDate: NgbDate = {
        year: 2022, month: 12, day: 20,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return false; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return true; }
      }
      let eventsAPISpy = spyOn(component['eventServ'], 'getRealEventsToken').and.returnValue(of({
        data: [
          { id: 1, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: '' },
          {
            id: 2, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: '',
            firelyr: [{ id: 1, fireid: 1, design: '', glyr: '', slug: '', store: '', style: '', work: '' }],
            freg: [{ fid: 1, code: '', name: '', munid: 1 }],
            mun: [{ fid: 1, code: '', name: '', nutiii: '' }]
          },
          {
            id: 3, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: '',
            firelyr: null, freg: null, mun: null
          },
        ]
      }));
      component.fromDate = fromDate;
      fixture.detectChanges();

      component.onDateSelection(newDate);

      expect(dateSpy).toHaveBeenCalled();
      expect(component.fromDate).toEqual(fromDate);
      expect(component.toDate).toEqual(newDate);
      expect(eventsAPISpy).toHaveBeenCalled();
      expect(updateRowSpy).toHaveBeenCalled();
    });

    it('T20.1.4 should handle error from filtering events by selected date range', () => {
      let dateSpy = spyOn(component, 'onDateSelection').and.callThrough();
      let updateRowSpy = spyOn(component, 'updateRowCount');
      let fromDate: NgbDate = {
        year: 2022, month: 12, day: 15,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return false; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return false; }
      }
      let newDate: NgbDate = {
        year: 2022, month: 12, day: 20,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return false; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return true; }
      }
      let eventsAPISpy = spyOn(component['eventServ'], 'getRealEventsToken').and.returnValue(throwError(() => new Error()));
      component.fromDate = fromDate;
      fixture.detectChanges();

      component.onDateSelection(newDate);

      expect(dateSpy).toHaveBeenCalled();
      expect(component.fromDate).toEqual(fromDate);
      expect(component.toDate).toEqual(newDate);
      expect(eventsAPISpy).toHaveBeenCalled();
      expect(updateRowSpy).not.toHaveBeenCalled();
    });

    it('T20.1.5 should check hovered date', () => {
      let hoveredSpy = spyOn(component, 'isHovered').and.callThrough();
      let fromDate: NgbDate = {
        year: 2022, month: 12, day: 15,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return false; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return false; }
      }
      let date: NgbDate = {
        year: 2022,
        month: 12,
        day: 15,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return true; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return true; }
      }
      component.fromDate = fromDate;
      component.toDate = null;
      component.hoveredDate = date;
      fixture.detectChanges();

      let result = component.isHovered(date);

      expect(hoveredSpy).toHaveBeenCalled();
      expect(result).toBeTrue();
    });
  });

  describe('TS20.2 filter real events by location', () => {
    it('T20.2.1 should receive map for location filtering and set onClick method', () => {
      let receiveSpy = spyOn(component, 'receiveFilterMap').and.callThrough();
      component.showFilterMap = true;
      fixture.detectChanges();
      expect(receiveSpy).toHaveBeenCalled();
      expect(component.filterMap).not.toBeNull();
    });

    it('T20.2.2 should detect click on location filter map', fakeAsync(() => {
      let polylineSpy = spyOn(component, 'createPolyline');
      component.showFilterMap = true;
      fixture.detectChanges();

      // click on map
      let map = fixture.debugElement.query(By.css('#filter-map-real')).nativeElement;
      map.click();
      tick();

      // expectations
      expect(polylineSpy).toHaveBeenCalled();
    }));

    it('T20.2.3 should initialize line group', () => {
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

    it('T20.2.4 should add polygon when last point is added', () => {
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

    it('T20.2.5 should clear map when clicked after all points are added', () => {
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

    it('T20.2.6 should toggle map when dropdown menu is open/closed', () => {
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

    it('T20.2.7 should clear location filter', () => {
      let clearSpy = spyOn(component, 'clearLocFilter').and.callThrough();
      let markerSpy = spyOn(component['markerServ'], 'clearPolyGroup');

      component.clearLocFilter();

      // expectations
      expect(clearSpy).toHaveBeenCalled();
      expect(component.filterPoints).toEqual([]);
      expect(markerSpy).toHaveBeenCalled();
    });

    it('T20.2.8 should filter real events by location', () => {
      let filterSpy = spyOn(component, 'filterLoc').and.callThrough();
      let eventsAPISpy = spyOn(component['eventServ'], 'getRealEventsToken').and.returnValue(of({
        data: [
          { id: 1, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: '' },
          {
            id: 2, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: '',
            firelyr: [{ id: 1, fireid: 1, design: '', glyr: '', slug: '', store: '', style: '', work: '' }],
            freg: [{ fid: 1, code: '', name: '', munid: 1 }],
            mun: [{ fid: 1, code: '', name: '', nutiii: '' }]
          },
          {
            id: 3, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: '',
            firelyr: null, freg: null, mun: null
          },
        ]
      }));
      let updateRowSpy = spyOn(component, 'updateRowCount');

      component.filterPoints = [[1, 1], [1, 1], [1, 1], [1, 1]];
      fixture.detectChanges();

      component.filterLoc();

      // expectations
      expect(filterSpy).toHaveBeenCalled();
      expect(eventsAPISpy).toHaveBeenCalled();
      expect(updateRowSpy).toHaveBeenCalled();
    });

    it('T20.2.9 should handle error from filtering real events by location', () => {
      let filterSpy = spyOn(component, 'filterLoc').and.callThrough();
      let eventsAPISpy = spyOn(component['eventServ'], 'getRealEventsToken').and.returnValue(throwError(() => new Error()));
      let updateRowSpy = spyOn(component, 'updateRowCount');

      component.filterPoints = [[1, 1], [1, 1], [1, 1], [1, 1]];
      fixture.detectChanges();

      component.filterLoc();

      // expectations
      expect(filterSpy).toHaveBeenCalled();
      expect(eventsAPISpy).toHaveBeenCalled();
      expect(updateRowSpy).not.toHaveBeenCalled();
    });
  });

  it('T20.6 should open real event details view', () => {
    // fake data
    let events: RealEvent[] = [
      {
        id: 1, name: null, type: null, startTime: '', endTime: '', geom: null,
        cause: null, codSGIF: null, codNCCO: null, burnedArea: 0, fireLayers: null, freg: null, mun: null
      }
    ];
    component.events = events;
    fixture.detectChanges();

    // spies
    let eventViewSpy = spyOn(component, 'toggleEventView').and.callThrough();

    component.toggleEventView(1);

    // expectations
    expect(eventViewSpy).toHaveBeenCalledWith(1);
    expect(component.isEventOpen).toBeTrue();
    expect(component.displayedHeaders).toEqual(component.openHeaders);
    expect(component.openEvent).toEqual(events[0]);
  });

  it('T20.7 should close real event details view', () => {
    // fake data
    let events: RealEvent[] = [
      {
        id: 1, name: null, type: null, startTime: '', endTime: '', geom: null,
        cause: null, codSGIF: null, codNCCO: null, burnedArea: 0, fireLayers: null, freg: null, mun: null
      }
    ];
    component.events = events;
    fixture.detectChanges();

    // spies
    let eventViewSpy = spyOn(component, 'toggleEventView').and.callThrough();

    component.toggleEventView(-1);

    // expectations
    expect(eventViewSpy).toHaveBeenCalledWith(-1);
    expect(component.isEventOpen).toBeFalse();
    expect(component.displayedHeaders).toEqual(component.headers);
  });

  it('T20.8 should toggle real event map', () => {
    // spies
    let toggleSpy = spyOn(component, 'toggleMapInfo').and.callThrough();

    component.toggleMapInfo();
    component.toggleMapInfo();

    // expectations
    expect(toggleSpy).toHaveBeenCalledTimes(2);
    expect(component.isMapVisible).toBeFalse();
  });

  it('T20.9 should receive map for real event display', () => {
    let receiveSpy = spyOn(component, 'receiveMap').and.callThrough();
    component.isMapVisible = true;
    fixture.detectChanges();

    component.receiveMap(null);
    component.receiveMap({});

    expect(receiveSpy).toHaveBeenCalled();
    expect(component.map).not.toBeNull();
  });

  describe('TS20.3 should open modal according to type', () => {
    it('T20.3.1 type: new', () => {
      // spies
      let openSpy = spyOn(component, 'open').and.callThrough();
      let modalSpy = spyOn(component['modalService'], 'open');

      component.open({}, 'new');

      // expectations
      expect(openSpy).toHaveBeenCalledWith({}, 'new');
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T20.3.2 type: edit', () => {
      // spies
      let openSpy = spyOn(component, 'open').and.callThrough();
      let initSpy = spyOn(component, 'initEditData');
      let modalSpy = spyOn(component['modalService'], 'open');

      component.open({}, 'edit');

      // expectations
      expect(openSpy).toHaveBeenCalledWith({}, 'edit');
      expect(initSpy).toHaveBeenCalledWith();
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T20.3.3 type: delete', () => {
      // spies
      let openSpy = spyOn(component, 'open').and.callThrough();
      let modalSpy = spyOn(component['modalService'], 'open');

      component.open({}, 'delete');

      // expectations
      expect(openSpy).toHaveBeenCalledWith({}, 'delete');
      expect(component.isConfChecked).toBeFalse();
      expect(component.hasClickedRemove).toBeFalse();
      expect(modalSpy).toHaveBeenCalled();
    });
  });

  it('T20.10 should initialize data for edit real event form (real event with all optional attributes)', () => {
    // fake data
    let openEvent: RealEvent = {
      id: 0, name: null, type: null, startTime: '05 October 2011 14:48 UTC', endTime: '05 October 2011 14:48 UTC', geom: null,
      cause: null, codSGIF: null, codNCCO: null, burnedArea: 0, fireLayers: null, freg: null, mun: null
    };
    component.openEvent = openEvent;
    fixture.detectChanges();

    // spies
    let initSpy = spyOn(component, 'initEditData').and.callThrough();

    component.initEditData();

    // expectations
    expect(initSpy).toHaveBeenCalled();
    expect(component.openEvent).toEqual(openEvent);
  });

  describe('TS20.4 create a new real event', () => {
    it('T20.4.1 should not create a new real event if new real event form is invalid', () => {
      // spies
      let createSpy = spyOn(component, 'createNewEvent').and.callThrough();
      let addAPISpy = spyOn(component['eventServ'], 'addRealEvent');
      let getInfoSpy = spyOn(component, 'getEventData');
      let rowSpy = spyOn(component, 'updateRowCount');

      component.createNewEvent();

      // expectations
      expect(createSpy).toHaveBeenCalled();
      expect(addAPISpy).not.toHaveBeenCalled();
      expect(getInfoSpy).not.toHaveBeenCalled();
      expect(rowSpy).not.toHaveBeenCalled();
    });

    it('T20.4.2 should create a new real event (no optional data)', () => {
      // spies
      let createSpy = spyOn(component, 'createNewEvent').and.callThrough();
      let addAPISpy = spyOn(component['eventServ'], 'addRealEvent').and.returnValue(of({
        id: 1, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: ''
      }));
      let getInfoSpy = spyOn(component, 'getEventData');
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new event information
      component.newEventForm.patchValue({
        start: '2018-06-12T19:30', end: '2018-07-12T19:30', geom: 'geom', epsg: 4326, timezone: 'Europe/Lisbon',
        name: null, cause: null, type: null, codSGIF: null, codNCCO: null
      });
      fixture.detectChanges();

      component.createNewEvent();

      // expectations
      expect(createSpy).toHaveBeenCalled();
      expect(addAPISpy).toHaveBeenCalled();
      expect(getInfoSpy).toHaveBeenCalled();
      expect(rowSpy).toHaveBeenCalled();
    });

    it('T20.4.3 should create a new real event (optional data)', () => {
      // spies
      let createSpy = spyOn(component, 'createNewEvent').and.callThrough();
      let addAPISpy = spyOn(component['eventServ'], 'addRealEvent').and.returnValue(of({
        id: 1, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: ''
      }));
      let getInfoSpy = spyOn(component, 'getEventData');
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new event information
      component.newEventForm.patchValue({
        start: '2018-06-12T19:30', end: '2018-07-12T19:30', geom: 'geom', epsg: 4326, timezone: 'Europe/Lisbon',
        name: 'name', cause: 'cause', type: 'type', codSGIF: 'cod', codNCCO: 'cod'
      });
      fixture.detectChanges();

      component.createNewEvent();

      // expectations
      expect(createSpy).toHaveBeenCalled();
      expect(addAPISpy).toHaveBeenCalled();
      expect(getInfoSpy).toHaveBeenCalled();
      expect(rowSpy).toHaveBeenCalled();
    });

    it('T20.4.4 should check form controls before creating a new real event', () => {
      // change form to test (coverage purposes only)
      component.newEventForm = new FormGroup({ fakeEmail: new FormControl('', []) });
      fixture.detectChanges();
      // spies
      let createSpy = spyOn(component, 'createNewEvent').and.callThrough();
      let addAPISpy = spyOn(component['eventServ'], 'addRealEvent').and.returnValue(of({
        id: 1, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: ''
      }));
      let getInfoSpy = spyOn(component, 'getEventData');
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new event information
      component.newEventForm.patchValue({
        start: '2018-06-12T19:30', end: '2018-07-12T19:30', geom: 'geom', epsg: 4326, timezone: 'Europe/Lisbon',
        name: 'name', cause: 'cause', type: 'type', codSGIF: 'cod', codNCCO: 'cod'
      });
      fixture.detectChanges();

      component.createNewEvent();

      // expectations
      expect(createSpy).toHaveBeenCalled();
      expect(addAPISpy).toHaveBeenCalled();
      expect(getInfoSpy).toHaveBeenCalled();
      expect(rowSpy).toHaveBeenCalled();
    });

    it('T20.4.5 should handle error from creating a new real event', () => {
      // spies
      let createSpy = spyOn(component, 'createNewEvent').and.callThrough();
      let addAPISpy = spyOn(component['eventServ'], 'addRealEvent').and.returnValue(throwError(() => new Error()));
      let getInfoSpy = spyOn(component, 'getEventData');
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new event information
      component.newEventForm.patchValue({
        start: '2018-06-12T19:30', end: '2018-07-12T19:30', geom: 'geom', epsg: 4326, timezone: 'Europe/Lisbon',
        name: 'name', cause: 'cause', type: 'type', codSGIF: 'cod', codNCCO: 'cod'
      });
      fixture.detectChanges();

      component.createNewEvent();

      // expectations
      expect(createSpy).toHaveBeenCalled();
      expect(addAPISpy).toHaveBeenCalled();
      expect(getInfoSpy).not.toHaveBeenCalled();
      expect(rowSpy).not.toHaveBeenCalled();
    });
  });

  describe('TS20.5 update a real event', () => {
    it('T20.5.1 should not update a real event if edit real event form is invalid', () => {
      // spies
      let updateSpy = spyOn(component, 'updateEvent').and.callThrough();
      let updateAPISpy = spyOn(component['eventServ'], 'updateRealEvent');

      component.updateEvent();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).not.toHaveBeenCalled();
    });

    it('T20.5.2 should update a real event (no optional data)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateEvent').and.callThrough();
      let updateAPISpy = spyOn(component['eventServ'], 'updateRealEvent').and.returnValue(of({
        id: 1, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: ''
      }));

      // fake edit event information
      component.editEventForm.patchValue({
        start: '2018-06-12T19:30', end: '2018-07-12T19:30', timezone: 'Europe/Lisbon',
        name: null, cause: null, type: null, codSGIF: null, codNCCO: null
      });
      let events: RealEvent[] = [
        {
          id: 1, name: null, type: null, startTime: '', endTime: '', geom: null,
          cause: null, codSGIF: null, codNCCO: null, burnedArea: 0, fireLayers: null, freg: null, mun: null
        }
      ];
      component.events = events;
      component.openEvent = events[0];
      fixture.detectChanges();

      component.updateEvent();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).toHaveBeenCalled();
    });

    it('T20.5.3 should update a real event (optional data)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateEvent').and.callThrough();
      let updateAPISpy = spyOn(component['eventServ'], 'updateRealEvent').and.returnValue(of({
        id: 1, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: ''
      }));

      // fake edit event information
      component.editEventForm.patchValue({
        start: '2018-06-12T19:30', end: '2018-07-12T19:30', timezone: 'Europe/Lisbon',
        name: 'name', cause: 'cause', type: 'type', codSGIF: 'cod', codNCCO: 'cod'
      });
      let events: RealEvent[] = [
        {
          id: 1, name: null, type: null, startTime: '', endTime: '', geom: null,
          cause: null, codSGIF: null, codNCCO: null, burnedArea: 0, fireLayers: null, freg: null, mun: null
        }
      ];
      component.events = events;
      component.openEvent = events[0];
      fixture.detectChanges();

      component.updateEvent();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).toHaveBeenCalled();
    });

    it('T20.5.4 should check form controls before updating real event', () => {
      // change form to test (coverage purposes only)
      component.editEventForm = new FormGroup({ fakeEmail: new FormControl('', []) });
      fixture.detectChanges();

      // spies
      let updateSpy = spyOn(component, 'updateEvent').and.callThrough();
      let updateAPISpy = spyOn(component['eventServ'], 'updateRealEvent').and.returnValue(of({
        id: 1, name: '', tipo: '', start: '', end: '', geom: '', causa: '', codsgif: '', codncco: '', burnedarea: ''
      }));

      // fake edit event information
      component.editEventForm.patchValue({
        start: '2018-06-12T19:30', end: '2018-07-12T19:30', timezone: 'Europe/Lisbon',
        name: 'name', cause: 'cause', type: 'type', codSGIF: 'cod', codNCCO: 'cod'
      });
      let events: RealEvent[] = [
        {
          id: 1, name: null, type: null, startTime: '', endTime: '', geom: null,
          cause: null, codSGIF: null, codNCCO: null, burnedArea: 0, fireLayers: null, freg: null, mun: null
        }
      ];
      component.events = events;
      component.openEvent = events[0];
      fixture.detectChanges();

      component.updateEvent();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).toHaveBeenCalled();
    });

    it('T20.5.5 should handle error from updating a real event', () => {
      // spies
      let updateSpy = spyOn(component, 'updateEvent').and.callThrough();
      let updateAPISpy = spyOn(component['eventServ'], 'updateRealEvent').and.returnValue(throwError(() => new Error()));

      // fake edit event information
      component.editEventForm.patchValue({
        start: '2018-06-12T19:30', end: '2018-07-12T19:30', timezone: 'Europe/Lisbon',
        name: 'name', cause: 'cause', type: 'type', codSGIF: 'cod', codNCCO: 'cod'
      });
      let events: RealEvent[] = [
        {
          id: 1, name: null, type: null, startTime: '', endTime: '', geom: null,
          cause: null, codSGIF: null, codNCCO: null, burnedArea: 0, fireLayers: null, freg: null, mun: null
        }
      ];
      component.events = events;
      component.openEvent = events[0];
      fixture.detectChanges();

      component.updateEvent();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).toHaveBeenCalled();
    });
  });

  describe('TS20.6 delete a real event', () => {
    it('T20.6.1 should not delete real event without confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeEvent').and.callThrough();
      let deleteAPISpy = spyOn(component['eventServ'], 'deleteRealEvent');

      component.removeEvent();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).not.toHaveBeenCalled();
    });

    it('T20.6.2 should delete real event information if there was confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeEvent').and.callThrough();
      let deleteAPISpy = spyOn(component['eventServ'], 'deleteRealEvent').and.returnValue(of({}));
      let rowSpy = spyOn(component, 'updateRowCount');

      let events: RealEvent[] = [
        {
          id: 1, name: null, type: null, startTime: '', endTime: '', geom: null,
          cause: null, codSGIF: null, codNCCO: null, burnedArea: 0, fireLayers: null, freg: null, mun: null
        }
      ];
      component.events = events;
      component.openEvent = events[0];
      component.isConfChecked = true;
      fixture.detectChanges();

      component.removeEvent();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).toHaveBeenCalled();
      expect(component.events).toEqual([]);
      expect(rowSpy).toHaveBeenCalledWith(0);
    });

    it('T20.6.3 should handle error on deleting real event information if there was confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeEvent').and.callThrough();
      let deleteAPISpy = spyOn(component['eventServ'], 'deleteRealEvent').and.returnValue(throwError(() => new Error()));
      let rowSpy = spyOn(component, 'updateRowCount');

      let events: RealEvent[] = [
        {
          id: 1, name: null, type: null, startTime: '', endTime: '', geom: null,
          cause: null, codSGIF: null, codNCCO: null, burnedArea: 0, fireLayers: null, freg: null, mun: null
        }
      ];
      component.events = events;
      component.openEvent = events[0];
      component.isConfChecked = true;
      fixture.detectChanges();

      component.removeEvent();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).toHaveBeenCalled();
      expect(component.events).toEqual(events);
      expect(rowSpy).not.toHaveBeenCalled();
    });
  });

});
