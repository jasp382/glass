import { Component } from '@angular/core';
import { By } from '@angular/platform-browser';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

// Testing
import { ComponentFixture, TestBed } from '@angular/core/testing';

// Interfaces
import { TableHeader } from 'src/app/interfaces/backoffice';

// Components
import { TableComponent } from './table.component';

// Mock Host Component
@Component({
  template: `
  <feat-table 
    [component]="component"
    [data]="data"
    [headers]="headers"
    [page]="page"
    [pageSize]="pageSize"
    [searchFilter]="searchFilter"
  ></feat-table>`
})
class TestHostComponent {
  component!: string;
  data!: any[];
  headers!: TableHeader[];
  page!: number;
  pageSize!: number;
  searchFilter!: string;
}

describe('TS26 TableComponent', () => {
  // table 
  let tableComponent: TableComponent;

  // fake host
  let hostComponent: TestHostComponent;
  let hostFixture: ComponentFixture<TestHostComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TableComponent, TestHostComponent],
      imports: [FontAwesomeModule,],
    }).compileComponents();

    hostFixture = TestBed.createComponent(TestHostComponent);
    hostComponent = hostFixture.componentInstance;

    tableComponent = hostFixture.debugElement.query(By.directive(TableComponent)).componentInstance;

    // defaults
    hostComponent.data = [];

    hostFixture.detectChanges();
  });

  it('T26.1 should create host component', () => { expect(hostComponent).toBeTruthy(); });

  it('T26.2 should create table component', () => { expect(tableComponent).toBeTruthy(); });

  describe('TS26.1 should detect changes in search filter', () => {
    it('T26.1.1 should detect changes in user search filter', () => {
      // spies
      let changesSpy = spyOn(tableComponent, 'ngOnChanges').and.callThrough();
      let filterUsersSpy = spyOn(tableComponent, 'filterDataSearchUsers');

      // change values
      hostComponent.component = 'users'
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      expect(changesSpy).toHaveBeenCalled();
      expect(filterUsersSpy).toHaveBeenCalled();
    });

    it('T26.1.2 should detect changes in group search filter', () => {
      // spies
      let changesSpy = spyOn(tableComponent, 'ngOnChanges').and.callThrough();
      let filterGroupsSpy = spyOn(tableComponent, 'filterDataSearchGroups');

      // change values
      hostComponent.component = 'groups-groups'
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      expect(changesSpy).toHaveBeenCalled();
      expect(filterGroupsSpy).toHaveBeenCalled();
    });

    it('T26.1.3 should detect changes in contribs search filter', () => {
      // spies
      let changesSpy = spyOn(tableComponent, 'ngOnChanges').and.callThrough();
      let filterContribsSpy = spyOn(tableComponent, 'filterDataSearchContributions');

      // change values
      hostComponent.component = 'contribs'
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      expect(changesSpy).toHaveBeenCalled();
      expect(filterContribsSpy).toHaveBeenCalled();
    });

    it('T26.1.4 should detect changes in events search filter', () => {
      // spies
      let changesSpy = spyOn(tableComponent, 'ngOnChanges').and.callThrough();
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchEvents');

      // change values
      hostComponent.component = 'events'
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      expect(changesSpy).toHaveBeenCalled();
      expect(filterEventsSpy).toHaveBeenCalled();
    });

    it('T26.1.5 should detect changes in real events search filter', () => {
      // spies
      let changesSpy = spyOn(tableComponent, 'ngOnChanges').and.callThrough();
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchRealEvents');

      // change values
      hostComponent.component = 'real-events'
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      expect(changesSpy).toHaveBeenCalled();
      expect(filterEventsSpy).toHaveBeenCalled();
    });

    it('T26.1.6 should detect changes in graphs search filter', () => {
      // spies
      let changesSpy = spyOn(tableComponent, 'ngOnChanges').and.callThrough();
      let filterSpy = spyOn(tableComponent, 'filterDataSearchGraphs');

      // change values
      hostComponent.component = 'graphs'
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      expect(changesSpy).toHaveBeenCalled();
      expect(filterSpy).toHaveBeenCalled();
    });

    it('T26.1.7 should detect changes in satellite search filter', () => {
      // spies
      let changesSpy = spyOn(tableComponent, 'ngOnChanges').and.callThrough();
      let filterSpy = spyOn(tableComponent, 'filterDataSearchSatellite');

      // change values
      hostComponent.component = 'satellite'
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      expect(changesSpy).toHaveBeenCalled();
      expect(filterSpy).toHaveBeenCalled();
    });

    it('T26.1.8 should detect changes in raster search filter', () => {
      // spies
      let changesSpy = spyOn(tableComponent, 'ngOnChanges').and.callThrough();
      let filterSpy = spyOn(tableComponent, 'filterDataSearchRaster');

      // change values
      hostComponent.component = 'raster'
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      expect(changesSpy).toHaveBeenCalled();
      expect(filterSpy).toHaveBeenCalled();
    });

    it('T26.1.9 should detect changes in vector search filter', () => {
      // spies
      let changesSpy = spyOn(tableComponent, 'ngOnChanges').and.callThrough();
      let filterSpy = spyOn(tableComponent, 'filterDataSearchVector');

      // change values
      hostComponent.component = 'vector'
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      expect(changesSpy).toHaveBeenCalled();
      expect(filterSpy).toHaveBeenCalled();
    });
  });

  it('T26.3 should detect changes in data', () => {
    // spies
    let changesSpy = spyOn(tableComponent, 'ngOnChanges').and.callThrough();

    // change values
    hostComponent.data = ['test'];
    hostFixture.detectChanges();

    expect(changesSpy).toHaveBeenCalled();
    expect(hostComponent.data).toEqual(['test']);
  });

  it('T26.4 should not select row when an icon on the row is clicked', () => {
    // setup spies
    let selectRowSpy = spyOn(tableComponent, 'selectRow').and.callThrough();
    let IDEmitterSpy = spyOn(tableComponent.selectedIDEmitter, 'emit');

    // test data
    let fakeEventSVG = { target: { tagName: 'svg' } };
    let fakeEventPath = { target: { tagName: 'path' } };

    tableComponent.selectRow({}, fakeEventSVG);
    tableComponent.selectRow({}, fakeEventPath);

    expect(selectRowSpy).toHaveBeenCalledTimes(2);
    expect(IDEmitterSpy).not.toHaveBeenCalled();
  });

  it('T26.5 should select row when clicked (not an icon)', () => {
    // setup spies
    let selectRowSpy = spyOn(tableComponent, 'selectRow').and.callThrough();
    let IDEmitterSpy = spyOn(tableComponent.selectedIDEmitter, 'emit');

    // test data
    hostComponent.data = [{ id: 1, open: false }];
    hostFixture.detectChanges();

    let fakeEvent = { target: { tagName: '' } };
    let fakeDataObj = { id: 1, open: false };
    tableComponent.selectRow(fakeDataObj, fakeEvent);

    // expectations
    expect(selectRowSpy).toHaveBeenCalledOnceWith(fakeDataObj, fakeEvent);
    expect(tableComponent.selectedRowID).toBe(1);
    expect(tableComponent.data).toEqual([{ id: 1, open: true }]);
    expect(tableComponent.filteredData).toEqual([{ id: 1, open: true }]);
    expect(IDEmitterSpy).toHaveBeenCalledOnceWith(1);
  });

  it('T26.6 should deselect row when clicked and row was selected (not an icon)', () => {
    // setup spies
    let selectRowSpy = spyOn(tableComponent, 'selectRow').and.callThrough();
    let IDEmitterSpy = spyOn(tableComponent.selectedIDEmitter, 'emit');

    // test data
    hostComponent.data = [{ id: 1, open: true }];
    tableComponent.selectedRowID = 1;
    hostFixture.detectChanges();

    let fakeEvent = { target: { tagName: '' } };
    let fakeDataObj = { id: 1, open: true };
    tableComponent.selectRow(fakeDataObj, fakeEvent);

    // expectations
    expect(selectRowSpy).toHaveBeenCalledOnceWith(fakeDataObj, fakeEvent);
    expect(tableComponent.selectedRowID).toBe(-1);
    expect(tableComponent.data).toEqual([{ id: 1, open: false }]);
    expect(tableComponent.filteredData).toEqual([{ id: 1, open: false }]);
    expect(IDEmitterSpy).toHaveBeenCalledOnceWith(-1);
  });

  describe('TS26.2 sort data by header', () => {
    it('T26.2.1 should sort data by header [start sort]', () => {
      // setup spies
      let sortSpy = spyOn(tableComponent, 'sortHeader').and.callThrough();

      // test data
      hostComponent.headers = [
        { columnLabel: '', objProperty: 'id' },
        { columnLabel: '', objProperty: 'group' },
        { columnLabel: '', objProperty: 'email' },
        { columnLabel: '', objProperty: 'name' },
        { columnLabel: '', objProperty: 'lastName' },
      ]
      hostComponent.data = [
        { id: 2, email: 'email', name: 'name', lastName: 'lastName' },
        { id: 1, email: 'a', name: 'b', lastName: 'c' },
      ];
      hostFixture.detectChanges();

      tableComponent.sortHeader(0);

      // expectations
      expect(sortSpy).toHaveBeenCalledOnceWith(0);
      expect(tableComponent.sortDir).toBe('desc');
      expect(tableComponent.selectedHeader).toBe(0);
      expect(tableComponent.filteredData).toEqual(
        [
          { id: 1, email: 'a', name: 'b', lastName: 'c' },
          { id: 2, email: 'email', name: 'name', lastName: 'lastName' },
        ]
      );
    });

    it('T26.2.2 should sort data by header [toggle sort]', () => {
      // setup spies
      let sortSpy = spyOn(tableComponent, 'sortHeader').and.callThrough();

      // test data
      hostComponent.headers = [
        { columnLabel: '', objProperty: 'id' },
        { columnLabel: '', objProperty: 'group' },
        { columnLabel: '', objProperty: 'email' },
        { columnLabel: '', objProperty: 'name' },
        { columnLabel: '', objProperty: 'lastName' },
      ]
      hostComponent.data = [
        { id: 1, email: 'a', name: 'b', lastName: 'c' },
        { id: 2, email: 'email', name: 'name', lastName: 'lastName' },
      ];
      hostFixture.detectChanges();

      tableComponent.selectedHeader = 0;
      tableComponent.sortDir = 'desc';
      hostFixture.detectChanges();

      tableComponent.sortHeader(0);
      // expectations
      expect(sortSpy).toHaveBeenCalledWith(0);
      expect(tableComponent.sortDir).toBe('asc');
      expect(tableComponent.selectedHeader).toBe(0);
      expect(tableComponent.filteredData).toEqual(
        [
          { id: 2, email: 'email', name: 'name', lastName: 'lastName' },
          { id: 1, email: 'a', name: 'b', lastName: 'c' },
        ]
      );

      tableComponent.sortHeader(0);
      // expectations
      expect(sortSpy).toHaveBeenCalledWith(0);
      expect(tableComponent.sortDir).toBe('desc');
      expect(tableComponent.selectedHeader).toBe(0);
      expect(tableComponent.filteredData).toEqual(
        [
          { id: 1, email: 'a', name: 'b', lastName: 'c' },
          { id: 2, email: 'email', name: 'name', lastName: 'lastName' },
        ]
      );
    });

    it('T26.2.3 should sort data by header [sort method]', () => {
      // setup spies
      let sortSpy = spyOn(tableComponent, 'sortHeader').and.callThrough();

      // test data
      hostComponent.headers = [
        { columnLabel: '', objProperty: 'id' },
        { columnLabel: '', objProperty: 'group' },
        { columnLabel: '', objProperty: 'email' },
        { columnLabel: '', objProperty: 'name' },
        { columnLabel: '', objProperty: 'lastName' },
      ]
      hostComponent.data = [
        { id: 2, email: 'email', name: 'name', lastName: 'lastName' },
        { id: 1, email: 'a', name: 'b', lastName: 'c' },
      ];
      hostFixture.detectChanges();

      tableComponent.selectedHeader = 0;
      tableComponent.sortDir = 'desc';
      hostFixture.detectChanges();

      // asc -> a < b
      tableComponent.sortHeader(0);
      // expectations
      expect(sortSpy).toHaveBeenCalledWith(0);
      expect(tableComponent.sortDir).toBe('asc');
      expect(tableComponent.selectedHeader).toBe(0);
      expect(tableComponent.filteredData).toEqual(
        [
          { id: 2, email: 'email', name: 'name', lastName: 'lastName' },
          { id: 1, email: 'a', name: 'b', lastName: 'c' },
        ]
      );

      // desc -> a < b
      hostComponent.data = [
        { id: 1, email: 'a', name: 'b', lastName: 'c' },
        { id: 2, email: 'email', name: 'name', lastName: 'lastName' },
      ];
      hostFixture.detectChanges();

      tableComponent.sortHeader(0);
      // expectations
      expect(sortSpy).toHaveBeenCalledWith(0);
      expect(tableComponent.sortDir).toBe('desc');
      expect(tableComponent.selectedHeader).toBe(0);
      expect(tableComponent.filteredData).toEqual(
        [
          { id: 1, email: 'a', name: 'b', lastName: 'c' },
          { id: 2, email: 'email', name: 'name', lastName: 'lastName' },
        ]
      );

      // asc -> a = b
      hostComponent.data = [
        { id: 1, email: 'a', name: 'b', lastName: 'c' },
        { id: 1, email: 'email', name: 'name', lastName: 'lastName' },
      ];
      hostFixture.detectChanges();

      tableComponent.selectedHeader = 0;
      tableComponent.sortDir = 'desc';
      hostFixture.detectChanges();

      tableComponent.sortHeader(0);
      // expectations
      expect(sortSpy).toHaveBeenCalledWith(0);
      expect(tableComponent.sortDir).toBe('asc');
      expect(tableComponent.selectedHeader).toBe(0);
      expect(tableComponent.filteredData).toEqual(
        [
          { id: 1, email: 'a', name: 'b', lastName: 'c' },
          { id: 1, email: 'email', name: 'name', lastName: 'lastName' },
        ]
      );

      // desc -> a = b
      tableComponent.sortHeader(0);
      // expectations
      expect(sortSpy).toHaveBeenCalledWith(0);
      expect(tableComponent.sortDir).toBe('desc');
      expect(tableComponent.selectedHeader).toBe(0);
      expect(tableComponent.filteredData).toEqual(
        [
          { id: 1, email: 'a', name: 'b', lastName: 'c' },
          { id: 1, email: 'email', name: 'name', lastName: 'lastName' },
        ]
      );
    });
  });

  describe('TS26.3 users', () => {
    it('T26.3.1 should correctly filter user data with search filter', () => {
      // setup spies
      let filterUsersSpy = spyOn(tableComponent, 'filterDataSearchUsers').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { columnLabel: '', objProperty: 'id' },
        { columnLabel: '', objProperty: 'group' },
        { columnLabel: '', objProperty: 'email' },
        { columnLabel: '', objProperty: 'name' },
        { columnLabel: '', objProperty: 'lastName' },
      ]
      hostComponent.data = [
        { email: 'email', name: 'name', lastName: 'lastName' },
        { email: 'a', name: 'b', lastName: 'c' },
      ];
      hostComponent.searchFilter = 'e';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchUsers();

      // expectations
      expect(filterUsersSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('e');
      expect(tableComponent.filteredData).toEqual([
        { email: 'email', name: 'name', lastName: 'lastName' },
      ]);

    });

    it('T26.3.2 should correctly filter user data with search filter and open headers', () => {
      // setup spies
      let filterUsersSpy = spyOn(tableComponent, 'filterDataSearchUsers').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { columnLabel: '', objProperty: 'id' },
        { columnLabel: '', objProperty: 'group' },
        { columnLabel: '', objProperty: 'email' },
      ]
      hostComponent.data = [
        { email: 'email', name: 'name', lastName: 'lastName' },
        { email: 'a', name: 'b', lastName: 'c' },
      ];
      hostComponent.searchFilter = 'e';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchUsers();

      // expectations
      expect(filterUsersSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('e');
      expect(tableComponent.filteredData).toEqual([
        { email: 'email', name: 'name', lastName: 'lastName' },
      ]);

    });

    it('T26.3.3 should correctly filter user data without search filter', () => {
      // setup spies
      let filterUsersSpy = spyOn(tableComponent, 'filterDataSearchUsers').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { columnLabel: '', objProperty: 'id' },
        { columnLabel: '', objProperty: 'group' },
        { columnLabel: '', objProperty: 'email' },
        { columnLabel: '', objProperty: 'name' },
        { columnLabel: '', objProperty: 'lastName' },
      ]
      hostComponent.data = [
        { email: 'email', name: 'name', lastName: 'lastName' },
        { email: 'a', name: 'b', lastName: 'c' },
      ];
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchUsers();

      // expectations
      expect(filterUsersSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(2);
      expect(tableComponent.searchFilter).toBe('');
      expect(tableComponent.filteredData).toEqual([
        { email: 'email', name: 'name', lastName: 'lastName' },
        { email: 'a', name: 'b', lastName: 'c' },
      ]);

    });
  });

  describe('TS26.4 groups', () => {
    it('T26.4.1 should correctly filter group data with search filter', () => {
      // setup spies
      let filterGroupsSpy = spyOn(tableComponent, 'filterDataSearchGroups').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { columnLabel: '', objProperty: 'id' },
        { columnLabel: '', objProperty: 'group' },
      ]
      hostComponent.data = [
        { group: 'a' }, { group: 'b' },
      ];
      hostComponent.searchFilter = 'a';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchGroups();

      // expectations
      expect(filterGroupsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('a');
      expect(tableComponent.filteredData).toEqual([{ group: 'a' }]);
    });

    it('T26.4.2 should correctly filter group data without search filter', () => {
      // setup spies
      let filterGroupsSpy = spyOn(tableComponent, 'filterDataSearchGroups').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { columnLabel: '', objProperty: 'id' },
        { columnLabel: '', objProperty: 'group' },
      ]
      hostComponent.data = [
        { group: 'a' }, { group: 'b' },
      ];
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchGroups();

      // expectations
      expect(filterGroupsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(2);
      expect(tableComponent.searchFilter).toBe('');
      expect(tableComponent.filteredData).toEqual([{ group: 'a' }, { group: 'b' }]);
    });
  });

  describe('TS26.5 contributions', () => {
    it('T26.5.1 should correctly filter contribution data with search filter', () => {
      // setup spies
      let filterContribsSpy = spyOn(tableComponent, 'filterDataSearchContributions').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '' },
        { objProperty: 'place', columnLabel: '' },
        { objProperty: 'date', columnLabel: '' },
        { objProperty: 'fire', columnLabel: '' },
      ]
      hostComponent.data = [
        { place: 'p', fire: 'f' }, { place: 'q', fire: 'g' }
      ];
      hostComponent.searchFilter = 'q';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchContributions();

      // expectations
      expect(filterContribsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('q');
      expect(tableComponent.filteredData).toEqual([{ place: 'q', fire: 'g' }]);
    });

    it('T26.5.2 should correctly filter contribution data with search filter and open headers', () => {
      // setup spies
      let filterContribsSpy = spyOn(tableComponent, 'filterDataSearchContributions').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '' },
        { objProperty: 'place', columnLabel: '' },
        { objProperty: 'date', columnLabel: '' },
      ]
      hostComponent.data = [
        { place: 'p', fire: 'f' }, { place: 'q', fire: 'g' }
      ];
      hostComponent.searchFilter = 'q';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchContributions();

      // expectations
      expect(filterContribsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('q');
      expect(tableComponent.filteredData).toEqual([{ place: 'q', fire: 'g' }]);
    });

    it('T26.5.3 should correctly filter contribution data without search filter', () => {
      // setup spies
      let filterContribsSpy = spyOn(tableComponent, 'filterDataSearchContributions').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '' },
        { objProperty: 'place', columnLabel: '' },
        { objProperty: 'date', columnLabel: '' },
        { objProperty: 'fire', columnLabel: '' },
      ]
      hostComponent.data = [
        { place: 'p', fire: 'f' }, { place: 'q', fire: 'g' }
      ];
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchContributions();

      // expectations
      expect(filterContribsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(2);
      expect(tableComponent.searchFilter).toBe('');
      expect(tableComponent.filteredData).toEqual([{ place: 'p', fire: 'f' }, { place: 'q', fire: 'g' }]);
    });
  });

  describe('TS26.6 events', () => {
    it('T26.6.1 should correctly filter event data with search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchEvents').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'place', columnLabel: 'Localização' },
        { objProperty: 'duration', columnLabel: 'Duração' },
        { objProperty: 'dim', columnLabel: 'Dimensão' },
        { objProperty: 'freg', columnLabel: 'Freguesia' },
        { objProperty: 'mun', columnLabel: 'Município' },
      ]
      hostComponent.data = [
        { place: 'p', freg: 'f', mun: 'm' }, { place: 'a', freg: 'b', mun: 'c' }
      ];
      hostComponent.searchFilter = 'm';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchEvents();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('m');
      expect(tableComponent.filteredData).toEqual([{ place: 'p', freg: 'f', mun: 'm' }]);
    });

    it('T26.6.2 should correctly filter event data with search filter and open headers', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchEvents').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'place', columnLabel: 'Localização' },
        { objProperty: 'duration', columnLabel: 'Duração' },
        { objProperty: 'dim', columnLabel: 'Dimensão' },
      ]
      hostComponent.data = [
        { place: 'p', freg: 'f', mun: 'm' }, { place: 'a', freg: 'b', mun: 'c' }
      ];
      hostComponent.searchFilter = 'p';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchEvents();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('p');
      expect(tableComponent.filteredData).toEqual([{ place: 'p', freg: 'f', mun: 'm' }]);
    });

    it('T26.6.3 should correctly filter event data without search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchEvents').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'place', columnLabel: 'Localização' },
        { objProperty: 'duration', columnLabel: 'Duração' },
        { objProperty: 'dim', columnLabel: 'Dimensão' },
        { objProperty: 'freg', columnLabel: 'Freguesia' },
        { objProperty: 'mun', columnLabel: 'Município' },
      ]
      hostComponent.data = [
        { place: 'p', freg: 'f', mun: 'm' }, { place: 'a', freg: 'b', mun: 'c' }
      ];
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchEvents();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(2);
      expect(tableComponent.searchFilter).toBe('');
      expect(tableComponent.filteredData).toEqual([
        { place: 'p', freg: 'f', mun: 'm' }, { place: 'a', freg: 'b', mun: 'c' }
      ]);
    });
  });

  describe('TS26.7 real events', () => {
    it('T26.7.1 should correctly filter real event data with search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchRealEvents').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'name', columnLabel: 'Nome' },
        { objProperty: 'type', columnLabel: 'Tipo' },
        { objProperty: 'startTime', columnLabel: 'Início' },
        { objProperty: 'endTime', columnLabel: 'Fim' },
      ];
      hostComponent.data = [
        { name: 'a', type: 'p' }, { name: null, type: null }
      ];
      hostComponent.searchFilter = 'p';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchRealEvents();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('p');
      expect(tableComponent.filteredData).toEqual([{ name: 'a', type: 'p' }]);
    });

    it('T26.7.2 should correctly filter real event data with search filter and open headers', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchRealEvents').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'name', columnLabel: 'Nome' },
        { objProperty: 'type', columnLabel: 'Tipo' },
      ];
      hostComponent.data = [
        { name: 'p', type: 'f' }, { name: null, type: null }
      ];
      hostComponent.searchFilter = 'p';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchRealEvents();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('p');
      expect(tableComponent.filteredData).toEqual([{ name: 'p', type: 'f' }]);
    });

    it('T26.7.3 should correctly filter real event data without search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchRealEvents').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'name', columnLabel: 'Nome' },
        { objProperty: 'type', columnLabel: 'Tipo' },
        { objProperty: 'startTime', columnLabel: 'Início' },
        { objProperty: 'endTime', columnLabel: 'Fim' },
      ];
      hostComponent.data = [
        { name: 'p', type: 'f' }, { name: null, type: null }
      ];
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchRealEvents();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(2);
      expect(tableComponent.searchFilter).toBe('');
      expect(tableComponent.filteredData).toEqual([
        { name: 'p', type: 'f' }, { name: null, type: null }
      ]);
    });
  });

  describe('TS26.8 graphs', () => {
    it('T26.8.1 should correctly filter graph data with search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchGraphs').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'chartType', columnLabel: 'Tipo' },
        { objProperty: 'designation', columnLabel: 'Título' },
        { objProperty: 'description', columnLabel: 'Descrição' },
      ];
      hostComponent.data = [
        { designation: 'a', description: 'p' }, { designation: 'a', description: 'b' }
      ];
      hostComponent.searchFilter = 'p';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchGraphs();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('p');
      expect(tableComponent.filteredData).toEqual([{ designation: 'a', description: 'p' }]);
    });

    it('T26.8.2 should correctly filter graph data with search filter and open headers', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchGraphs').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'chartType', columnLabel: 'Tipo' },
        { objProperty: 'designation', columnLabel: 'Título' }
      ];
      hostComponent.data = [
        { designation: 'a', description: 'b' }, { designation: 'c', description: 'd' }
      ];
      hostComponent.searchFilter = 'c';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchGraphs();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('c');
      expect(tableComponent.filteredData).toEqual([{ designation: 'c', description: 'd' }]);
    });

    it('T26.8.3 should correctly filter graph data without search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchGraphs').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'chartType', columnLabel: 'Tipo' },
        { objProperty: 'designation', columnLabel: 'Título' },
        { objProperty: 'description', columnLabel: 'Descrição' },
      ];
      hostComponent.data = [
        { designation: 'a', description: 'p' }, { designation: 'a', description: 'b' }
      ];
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchGraphs();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(2);
      expect(tableComponent.searchFilter).toBe('');
      expect(tableComponent.filteredData).toEqual([
        { designation: 'a', description: 'p' }, { designation: 'a', description: 'b' }
      ]);
    });
  });

  describe('TS26.9 satellite', () => {
    it('T26.9.1 should correctly filter satellite dataset data with search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchSatellite').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'summary', columnLabel: 'Resumo' },
        { objProperty: 'title', columnLabel: 'Título' },
      ];
      hostComponent.data = [
        { summary: 'a', title: 'p' }, { summary: 'a', title: 'b' }
      ];
      hostComponent.searchFilter = 'p';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchSatellite();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('p');
      expect(tableComponent.filteredData).toEqual([{ summary: 'a', title: 'p' }]);
    });

    it('T26.9.2 should correctly filter satellite dataset data with search filter and open headers', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchSatellite').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'summary', columnLabel: 'Resumo' },
      ];
      hostComponent.data = [
        { summary: 'a', title: 'b' }, { summary: 'c', title: 'd' }
      ];
      hostComponent.searchFilter = 'c';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchSatellite();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('c');
      expect(tableComponent.filteredData).toEqual([{ summary: 'c', title: 'd' }]);
    });

    it('T26.9.3 should correctly filter satellite dataset data without search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchSatellite').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'summary', columnLabel: 'Resumo' },
        { objProperty: 'title', columnLabel: 'Título' },
      ];
      hostComponent.data = [
        { summary: 'a', title: 'b' }, { summary: 'c', title: 'd' }
      ];
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchSatellite();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(2);
      expect(tableComponent.searchFilter).toBe('');
      expect(tableComponent.filteredData).toEqual([
        { summary: 'a', title: 'b' }, { summary: 'c', title: 'd' }
      ]);
    });
  });

  describe('TS26.10 raster', () => {
    it('T26.10.1 should correctly filter raster dataset data with search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchRaster').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'name', columnLabel: 'Nome' },
        { objProperty: 'source', columnLabel: 'Fonte' },
        { objProperty: 'refYear', columnLabel: 'Ano Dados' },
        { objProperty: 'refProd', columnLabel: 'Ano Produção' },
      ];
      hostComponent.data = [
        { name: 'a', source: 'p' }, { name: 'a', source: 'b' }
      ];
      hostComponent.searchFilter = 'p';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchRaster();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('p');
      expect(tableComponent.filteredData).toEqual([{ name: 'a', source: 'p' }]);
    });

    it('T26.10.2 should correctly filter raster dataset data with search filter and open headers', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchRaster').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'name', columnLabel: 'Nome' },
        { objProperty: 'source', columnLabel: 'Fonte' },
      ];
      hostComponent.data = [
        { name: 'a', source: 'b' }, { name: 'c', source: 'd' }
      ];
      hostComponent.searchFilter = 'c';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchRaster();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('c');
      expect(tableComponent.filteredData).toEqual([{ name: 'c', source: 'd' }]);
    });

    it('T26.10.3 should correctly filter raster dataset data without search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchRaster').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'name', columnLabel: 'Nome' },
        { objProperty: 'source', columnLabel: 'Fonte' },
        { objProperty: 'refYear', columnLabel: 'Ano Dados' },
        { objProperty: 'refProd', columnLabel: 'Ano Produção' },
      ];
      hostComponent.data = [
        { name: 'a', source: 'b' }, { name: 'c', source: 'd' }
      ];
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchRaster();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(2);
      expect(tableComponent.searchFilter).toBe('');
      expect(tableComponent.filteredData).toEqual([
        { name: 'a', source: 'b' }, { name: 'c', source: 'd' }
      ]);
    });
  });

  describe('TS26.11 vector', () => {
    it('T26.11.1 should correctly filter vector dataset data with search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchVector').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'name', columnLabel: 'Nome' },
        { objProperty: 'source', columnLabel: 'Fonte' },
        { objProperty: 'refYear', columnLabel: 'Ano Dados' },
        { objProperty: 'refProd', columnLabel: 'Ano Produção' },
      ];
      hostComponent.data = [
        { name: 'a', source: 'p' }, { name: 'a', source: 'b' }
      ];
      hostComponent.searchFilter = 'p';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchVector();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('p');
      expect(tableComponent.filteredData).toEqual([{ name: 'a', source: 'p' }]);
    });

    it('T26.11.2 should correctly filter vector dataset data with search filter and open headers', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchVector').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'name', columnLabel: 'Nome' },
        { objProperty: 'source', columnLabel: 'Fonte' },
      ];
      hostComponent.data = [
        { name: 'a', source: 'b' }, { name: 'c', source: 'd' }
      ];
      hostComponent.searchFilter = 'c';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchVector();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(1);
      expect(tableComponent.searchFilter).toBe('c');
      expect(tableComponent.filteredData).toEqual([{ name: 'c', source: 'd' }]);
    });

    it('T26.11.3 should correctly filter vector dataset data without search filter', () => {
      // setup spies
      let filterEventsSpy = spyOn(tableComponent, 'filterDataSearchVector').and.callThrough();
      let rowCountEmitterSpy = spyOn(tableComponent.rowCountEmitter, 'emit');

      // test data
      hostComponent.headers = [
        { objProperty: 'id', columnLabel: '#' },
        { objProperty: 'name', columnLabel: 'Nome' },
        { objProperty: 'source', columnLabel: 'Fonte' },
        { objProperty: 'refYear', columnLabel: 'Ano Dados' },
        { objProperty: 'refProd', columnLabel: 'Ano Produção' },
      ];
      hostComponent.data = [
        { name: 'a', source: 'b' }, { name: 'c', source: 'd' }
      ];
      hostComponent.searchFilter = '';
      hostFixture.detectChanges();

      tableComponent.filterDataSearchVector();

      // expectations
      expect(filterEventsSpy).toHaveBeenCalledOnceWith();
      expect(rowCountEmitterSpy).toHaveBeenCalledOnceWith(2);
      expect(tableComponent.searchFilter).toBe('');
      expect(tableComponent.filteredData).toEqual([
        { name: 'a', source: 'b' }, { name: 'c', source: 'd' }
      ]);
    });
  });

  it('T26.7 should emit object ID on #editRow', () => {
    // setup spies
    let editRowSpy = spyOn(tableComponent, 'editRow').and.callThrough();
    let IDEmitterSpy = spyOn(tableComponent.rowEditIDEmitter, 'emit');

    // object to fake
    let object = { id: 15 };
    tableComponent.editRow(object);

    // expectations
    expect(editRowSpy).toHaveBeenCalledOnceWith(object);
    expect(IDEmitterSpy).toHaveBeenCalledOnceWith(object.id);
  });

  it('T26.8 should emit object ID on #deleteRow', () => {
    // setup spies
    let deleteRowSpy = spyOn(tableComponent, 'deleteRow').and.callThrough();
    let IDEmitterSpy = spyOn(tableComponent.rowDeleteIDEmitter, 'emit');

    // object to fake
    let object = { id: 15 };
    tableComponent.deleteRow(object);

    // expectations
    expect(deleteRowSpy).toHaveBeenCalledOnceWith(object);
    expect(IDEmitterSpy).toHaveBeenCalledOnceWith(object.id);
  });

});
