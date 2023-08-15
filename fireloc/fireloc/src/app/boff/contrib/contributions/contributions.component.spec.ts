import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbDate, NgbDateStruct, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FeatModule } from 'src/app/feat/feat.module';

import { ContributionsComponent } from './contributions.component';

describe('TS10 Backoffice ContributionsComponent', () => {
  let component: ContributionsComponent;
  let fixture: ComponentFixture<ContributionsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ContributionsComponent],
      imports: [
        FeatModule,
        FontAwesomeModule,
        NgbModule,
        FormsModule,
        ReactiveFormsModule,
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ContributionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T10.1 should create', () => { expect(component).toBeTruthy(); });

  it('T10.2 should update search terms', () => {
    // spies
    let searchSpy = spyOn(component, 'searchContribs').and.callThrough();

    component.searchContribs(null as unknown as string);
    component.searchContribs('search');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('search');
    expect(component.searchTerms).toEqual('search');
  });

  it('T10.3 should update data row count for pagination', () => {
    // setup
    let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();

    component.updateRowCount(10);

    // expectations
    expect(rowSpy).toHaveBeenCalledOnceWith(10);
    expect(component.rowCount).toBe(10);
  });

  it('T10.4 should get current page for table component', () => {
    // setup
    let pageSpy = spyOn(component, 'getPage').and.callThrough();

    component.getPage(5);

    // expectations
    expect(pageSpy).toHaveBeenCalledOnceWith(5);
    expect(component.currentPage).toBe(5);
  });

  it('T10.5 should search users by name in users filter', () => {
    // spies
    let searchSpy = spyOn(component, 'searchUsers').and.callThrough();

    component.searchUsers('');
    component.searchUsers('Raquel');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('Raquel');
    expect(component.userSearchTerms).toEqual('Raquel');
    expect(component.filteredUsers).toEqual([{ id: 2, name: 'Raquel Ferreira', email: 'fireloc@fireloc.com', selected: false }]);
  });

  // TODO UPDATE TESTS WHEN API AVAILABLE
  describe('TS10.1 filter contributions by location', () => {
    it('T10.1.1 should receive map for location filtering and set onClick method', () => {
      let receiveSpy = spyOn(component, 'receiveFilterMap').and.callThrough();
      component.showFilterMap = true;
      fixture.detectChanges();
      expect(receiveSpy).toHaveBeenCalled();
      expect(component.filterMap).not.toBeNull();
    });

    it('T10.1.2 should detect click on location filter map', fakeAsync(() => {
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

    it('T10.1.3 should initialize line group', () => {
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

    it('T10.1.4 should add polygon when last point is added', () => {
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

    it('T10.1.5 should clear map when clicked after all points are added', () => {
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

    it('T10.1.6 should toggle map when dropdown menu is open/closed', () => {
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

    it('T10.1.7 should clear location filter', () => {
      let clearSpy = spyOn(component, 'clearLocFilter').and.callThrough();
      let markerSpy = spyOn(component['markerServ'], 'clearPolyGroup');

      component.clearLocFilter();

      // expectations
      expect(clearSpy).toHaveBeenCalled();
      expect(component.filterPoints).toEqual([]);
      expect(markerSpy).toHaveBeenCalled();
    });

    it('T10.1.8 should filter real events by location', () => {
      let filterSpy = spyOn(component, 'filterLoc').and.callThrough();

      component.filterPoints = [[1, 1], [1, 1], [1, 1], [1, 1]];
      fixture.detectChanges();

      component.filterLoc();

      // expectations
      expect(filterSpy).toHaveBeenCalled();
    });
  });

  it('T10.6 should select user for contribution filtering', () => {
    // spies
    let searchSpy = spyOn(component, 'selectUser').and.callThrough();

    component.selectUser(2);

    // expectations
    expect(searchSpy).toHaveBeenCalledWith(2);
    expect(component.users[1].selected).toBeTrue();
    expect(component.filterUserEmail).toEqual('fireloc@fireloc.com');
  });

  // TODO UPDATE TESTS WHEN API AVAILABLE
  describe('TS10.2 filter contributions by date', () => {
    it('T10.2.1 should select start date if no dates are selected', () => {
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

    it('T10.2.2 should renew start date if dates are selected but new date is before the set start date', () => {
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

    it('T10.2.3 should filter contributions by selected date range', () => {
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

    it('T10.2.4 should check hovered date', () => {
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
  it('T10.7 should open contribution details view', () => {
    // spies
    let contribViewSpy = spyOn(component, 'toggleContribView').and.callThrough();

    component.toggleContribView(1);

    // expectations
    expect(contribViewSpy).toHaveBeenCalledWith(1);
    expect(component.isContribOpen).toBeTrue();
    expect(component.displayedHeaders).toEqual(component.openHeaders);
    expect(component.openContrib).toEqual(component.contribs[0]);
  });

  // TODO UPDATE TESTS WHEN API AVAILABLE
  it('T10.8 should close contribution details view', () => {
    // spies
    let contribViewSpy = spyOn(component, 'toggleContribView').and.callThrough();

    component.toggleContribView(-1);

    // expectations
    expect(contribViewSpy).toHaveBeenCalledWith(-1);
    expect(component.isContribOpen).toBeFalse();
    expect(component.displayedHeaders).toEqual(component.headers);
  });

  it('T10.9 should toggle map for contribution', () => {
    let mapViewSpy = spyOn(component, 'toggleMapImage').and.callThrough();
    component.toggleMapImage(); // true
    component.toggleMapImage(); // false
    expect(mapViewSpy).toHaveBeenCalledTimes(2);
    expect(component.isMapVisible).toBeFalse();
  });

  it('T10.10 should receive map for contribution display', () => {
    let receiveSpy = spyOn(component, 'receiveMap').and.callThrough();
    let markerSpy = spyOn(component['markerServ'], 'addMarkerToMap')
    fixture.detectChanges();

    component.receiveMap(null);
    component.receiveMap({});

    expect(receiveSpy).toHaveBeenCalled();
    expect(component.map).not.toBeNull();
    expect(markerSpy).toHaveBeenCalled();
  });

  it('T10.11 should open modal', () => {
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

  // TODO UPDATE TESTS WHEN API AVAILABLE
  describe('TS10.3 delete a contribution', () => {
    it('T10.3.1 should not delete contribution without confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'deleteContrib').and.callThrough();

      component.deleteContrib();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
    });

    it('T10.3.2 should delete contribution information if there was confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'deleteContrib').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount');

      component.openContrib = component.contribs[0];
      component.isConfChecked = true;
      fixture.detectChanges();

      component.deleteContrib();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(component.contribs.length).toEqual(4);
      expect(rowSpy).toHaveBeenCalledWith(4);
      expect(component.isContribOpen).toBeFalse();
      expect(component.displayedHeaders).toEqual(component.headers);
    });
  });

});
