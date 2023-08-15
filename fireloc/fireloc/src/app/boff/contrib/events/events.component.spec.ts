import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbDate, NgbDateStruct, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FeatModule } from 'src/app/feat/feat.module';

import { EventsComponent } from './events.component';

describe('TS11 Backoffice EventsComponent', () => {
  let component: EventsComponent;
  let fixture: ComponentFixture<EventsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [EventsComponent],
      imports: [
        FeatModule,
        FontAwesomeModule,
        NgbModule
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(EventsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T11.1 should create', () => { expect(component).toBeTruthy(); });

  it('T11.2 should update search terms', () => {
    // spies
    let searchSpy = spyOn(component, 'searchEvents').and.callThrough();

    component.searchEvents(null as unknown as string);
    component.searchEvents('search');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('search');
    expect(component.searchTerms).toEqual('search');
  });

  it('T11.3 should update data row count for pagination', () => {
    // setup
    let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();

    component.updateRowCount(10);

    // expectations
    expect(rowSpy).toHaveBeenCalledOnceWith(10);
    expect(component.rowCount).toBe(10);
  });

  it('T11.4 should get current page for table component', () => {
    // setup
    let pageSpy = spyOn(component, 'getPage').and.callThrough();

    component.getPage(5);

    // expectations
    expect(pageSpy).toHaveBeenCalledOnceWith(5);
    expect(component.currentPage).toBe(5);
  });

  // TODO UPDATE TESTS WHEN API AVAILABLE
  describe('TS11.1 filter events by location', () => {
    it('T11.1.1 should receive map for location filtering and set onClick method', () => {
      let receiveSpy = spyOn(component, 'receiveFilterMap').and.callThrough();
      component.showFilterMap = true;
      fixture.detectChanges();
      expect(receiveSpy).toHaveBeenCalled();
      expect(component.filterMap).not.toBeNull();
    });

    it('T11.1.2 should detect click on location filter map', fakeAsync(() => {
      let polylineSpy = spyOn(component, 'createPolyline');
      component.showFilterMap = true;
      fixture.detectChanges();

      // click on map
      let map = fixture.debugElement.query(By.css('#filter-map')).nativeElement;
      map.click();
      tick();

      // expectations
      expect(polylineSpy).toHaveBeenCalled();
    }));

    it('T11.1.3 should initialize line group', () => {
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

    it('T11.1.4 should add polygon when last point is added', () => {
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

    it('T11.1.5 should clear map when clicked after all points are added', () => {
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

    it('T11.1.6 should toggle map when dropdown menu is open/closed', () => {
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

    it('T11.1.7 should clear location filter', () => {
      let clearSpy = spyOn(component, 'clearLocFilter').and.callThrough();
      let markerSpy = spyOn(component['markerServ'], 'clearPolyGroup');

      component.clearLocFilter();

      // expectations
      expect(clearSpy).toHaveBeenCalled();
      expect(component.filterPoints).toEqual([]);
      expect(markerSpy).toHaveBeenCalled();
    });

    it('T11.1.8 should filter real events by location', () => {
      let filterSpy = spyOn(component, 'filterLoc').and.callThrough();

      component.filterPoints = [[1, 1], [1, 1], [1, 1], [1, 1]];
      fixture.detectChanges();

      component.filterLoc();

      // expectations
      expect(filterSpy).toHaveBeenCalled();
    });
  });

  // TODO UPDATE TESTS WHEN API AVAILABLE
  describe('TS11.2 filter events by date', () => {
    it('T11.2.1 should select start date if no dates are selected', () => {
      let dateSpy = spyOn(component, 'onDateSelection').and.callThrough();
      let fromDate: NgbDate = {
        year: 2022,
        month: 12,
        day: 15,
        equals: function (other?: NgbDateStruct | null | undefined): boolean { return false },
        before: function (other?: NgbDateStruct | null | undefined): boolean { return false; },
        after: function (other?: NgbDateStruct | null | undefined): boolean { return true; }
      }
      component.onDateSelection(fromDate);

      expect(dateSpy).toHaveBeenCalled();
      expect(component.fromDate).toEqual(fromDate);
    });

    it('T11.2.2 should renew start date if dates are selected but new date is before the set start date', () => {
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
      component.fromDate = fromDate;
      component.toDate = toDate;
      fixture.detectChanges();

      component.onDateSelection(newDate);

      expect(dateSpy).toHaveBeenCalled();
      expect(component.fromDate).toEqual(newDate);
      expect(component.toDate).toBeNull();
    });

    it('T11.2.3 should filter events by selected date range', () => {
      let dateSpy = spyOn(component, 'onDateSelection').and.callThrough();
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
      component.fromDate = fromDate;
      fixture.detectChanges();

      component.onDateSelection(newDate);

      expect(dateSpy).toHaveBeenCalled();
      expect(component.fromDate).toEqual(fromDate);
      expect(component.toDate).toEqual(newDate);
    });

    it('T11.2.4 should check hovered date', () => {
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

  // TODO UPDATE TESTS WHEN API AVAILABLE
  it('T11.5 should open event details view', () => {
    // spies
    let eventViewSpy = spyOn(component, 'toggleEventView').and.callThrough();

    component.toggleEventView(1);

    // expectations
    expect(eventViewSpy).toHaveBeenCalledWith(1);
    expect(component.isEventOpen).toBeTrue();
    expect(component.selectedEventSection).toBe(1);
    expect(component.displayedHeaders).toEqual(component.openHeaders);
    expect(component.openEvent).toEqual(component.events[0]);
  });

  // TODO UPDATE TESTS WHEN API AVAILABLE
  it('T11.6 should close event details view', () => {
    // spies
    let eventViewSpy = spyOn(component, 'toggleEventView').and.callThrough();

    component.toggleEventView(-1);

    // expectations
    expect(eventViewSpy).toHaveBeenCalledWith(-1);
    expect(component.isEventOpen).toBeFalse();
    expect(component.displayedHeaders).toEqual(component.headers);
  });

  it('T11.7 should select event section for information to be displayed', () => {
    // spies
    let selectSpy = spyOn(component, 'selectEventSection').and.callThrough();

    component.selectEventSection(1);
    component.selectEventSection(2);
    expect(selectSpy).toHaveBeenCalled();
    expect(component.selectedEventSection).toBe(2);
  });

  it('T11.8 should receive map for event display', () => {
    let receiveSpy = spyOn(component, 'receiveMap').and.callThrough();
    let markerSpy = spyOn(component['markerServ'], 'addMarkerToMap')
    fixture.detectChanges();

    component.receiveMap(null);
    component.receiveMap({});

    expect(receiveSpy).toHaveBeenCalled();
    expect(component.map).not.toBeNull();
    expect(markerSpy).toHaveBeenCalled();
  });

  it('T11.9 should open modal', () => {
    // spies
    let openSpy = spyOn(component, 'open').and.callThrough();
    let modalSpy = spyOn(component['modalService'], 'open');

    component.open({});

    // expectations
    expect(openSpy).toHaveBeenCalledWith({});
    expect(component.isConfChecked).toBeFalse();
    expect(component.hasClickedRemove).toBeFalse();
    expect(modalSpy).toHaveBeenCalled();
  });

  it('T11.10 should update event information from edit input form', () => {
    // spies
    let updateSpy = spyOn(component, 'updateEditEventField').and.callThrough();
    component.updateEditEventField('newName', 'name');
    expect(updateSpy).toHaveBeenCalled();
    expect(component.editEvent.name).toEqual('newName');
  });

  // TODO UPDATE TESTS WHEN API AVAILABLE
  describe('TS11.3 update an event', () => {
    it('T11.3.1 should not update an event if edit event form is invalid', () => {
      // spies
      let updateSpy = spyOn(component, 'updateEvent').and.callThrough();

      component.updateEvent();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
    });

    it('T11.3.2 should update a real event', () => {
      // spies
      let updateSpy = spyOn(component, 'updateEvent').and.callThrough();

      // fake edit event information
      component.editEventForm.patchValue({
        name: 'name', place: 'place', start: '2018-06-12T19:30', end: '2018-07-12T19:30',
        type: 'type', cause: 'cause', geom: 'geom', codSGIF: 'cod', codNCCO: 'cod'
      });
      component.openEvent = component.events[0];
      fixture.detectChanges();

      component.updateEvent();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
    });
  });

  // TODO UPDATE TESTS WHEN API AVAILABLE
  describe('TS11.4 delete an event', () => {
    it('T11.4.1 should not delete event without confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'deleteEvent').and.callThrough();

      component.deleteEvent();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
    });

    it('T11.4.2 should delete event information if there was confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'deleteEvent').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount');

      component.openEvent = component.events[0];
      component.isConfChecked = true;
      fixture.detectChanges();

      component.deleteEvent();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(component.events.length).toEqual(4);
      expect(rowSpy).toHaveBeenCalledWith(4);
      expect(component.isEventOpen).toBeFalse();
      expect(component.displayedHeaders).toEqual(component.headers);
    });
  });

});
