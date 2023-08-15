import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormArray, FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { of, throwError } from 'rxjs';
import { FeatModule } from 'src/app/feat/feat.module';
import { GeoChart } from 'src/app/interfaces/graphs';

import { GraphsComponent } from './graphs.component';

describe('TS17 Backoffice GraphsComponent', () => {
  let component: GraphsComponent;
  let fixture: ComponentFixture<GraphsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [GraphsComponent],
      imports: [
        HttpClientTestingModule,
        FeatModule,
        FontAwesomeModule
      ],
      providers: [FormBuilder]
    }).compileComponents();

    fixture = TestBed.createComponent(GraphsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T17.1 should create', () => { expect(component).toBeTruthy(); });

  it('T17.2 should get charts from API', () => {
    // setup
    let getSpy = spyOn(component, 'getCharts').and.callThrough();
    let getAPISpy = spyOn(component['chartServ'], 'getCharts')
      .and.returnValue(of({
        data: [{
          id: 1, slug: 'slug', designation: 'design', description: 'desc', chartype: 'BAR',
          series: [{ id: 1, slug: 'slug', name: 'name', color: '#000' }]
        },
        ]
      }));
    let dataSpy = spyOn(component, 'getChartsData').and.callThrough();
    let seriesSpy = spyOn(component, 'getSeriesData').and.callThrough();
    let rowSpy = spyOn(component, 'updateRowCount');

    component.getCharts();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).toHaveBeenCalled();
    expect(seriesSpy).toHaveBeenCalled();
    expect(rowSpy).toHaveBeenCalled();
    expect(component.charts.length).not.toBe(0);
  });

  it('T17.3 should handle error from getting charts from API', () => {
    // setup
    let getSpy = spyOn(component, 'getCharts').and.callThrough();
    let getAPISpy = spyOn(component['chartServ'], 'getCharts').and.returnValue(throwError(() => new Error()));
    let dataSpy = spyOn(component, 'getChartsData').and.callThrough();
    let seriesSpy = spyOn(component, 'getSeriesData').and.callThrough();
    let rowSpy = spyOn(component, 'updateRowCount');

    component.getCharts();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).not.toHaveBeenCalled();
    expect(seriesSpy).not.toHaveBeenCalled();
    expect(rowSpy).not.toHaveBeenCalled();
    expect(component.charts.length).toBe(0);
  });

  it('T17.4 should update search terms', () => {
    // spies
    let searchSpy = spyOn(component, 'searchCharts').and.callThrough();

    component.searchCharts(null as unknown as string);
    component.searchCharts('search');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('search');
    expect(component.searchTerms).toEqual('search');
  });

  it('T17.5 should filter charts by type', () => {
    // fake data
    let charts: GeoChart[] = [{
      id: 1, slug: '', designation: '', description: '', series: [], chartType: 'BAR'
    }];
    component.charts = charts;
    fixture.detectChanges();

    // spies
    let selectSpy = spyOn(component, 'selectType').and.callThrough();
    let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();

    component.selectType(1); // id:1 -> selected true
    component.selectType(1); // id:1 -> selected false

    // expectations
    expect(selectSpy).toHaveBeenCalledWith(1);
    expect(component.types[0].selected).toBeFalse();
    expect(component.selectedTypes).toEqual([]);
    expect(rowSpy).toHaveBeenCalled();
  });

  describe('TS17.1 should open modal according to type', () => {
    it('T17.1.1 type: new', () => {
      // spies
      let openSpy = spyOn(component, 'open').and.callThrough();
      let modalSpy = spyOn(component['modalService'], 'open');

      component.open({}, 'new');

      // expectations
      expect(openSpy).toHaveBeenCalledWith({}, 'new');
      expect(component.newChartType).toEqual('BAR');
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T17.1.2 type: edit', () => {
      // spies
      let openSpy = spyOn(component, 'open').and.callThrough();
      let initSpy = spyOn(component, 'initEditChart');
      let modalSpy = spyOn(component['modalService'], 'open');

      component.open({}, 'edit');

      // expectations
      expect(openSpy).toHaveBeenCalledWith({}, 'edit');
      expect(initSpy).toHaveBeenCalledWith();
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T17.1.3 type: delete', () => {
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

  it('T17.6 should initialize data for edit dataset form', () => {
    // fake data
    let openChart: GeoChart = {
      id: 1, slug: '', designation: '', description: '', chartType: 'BAR',
      series: [{ id: 1, slug: 'slug', name: 'name', color: '#000', points: [] }],
    };
    component.openChart = openChart;
    fixture.detectChanges();

    // spies
    let initSpy = spyOn(component, 'initEditChart').and.callThrough();

    component.initEditChart();

    // expectations
    expect(initSpy).toHaveBeenCalledWith();
    expect(component.editChart).toEqual(openChart);
  });

  it('T17.7 should update data row count for pagination', () => {
    // setup
    let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();
    component.updateRowCount(10);
    // expectations
    expect(rowSpy).toHaveBeenCalledOnceWith(10);
    expect(component.rowCount).toBe(10);
  });

  it('T17.8 should get current page for table component', () => {
    // setup
    let pageSpy = spyOn(component, 'getPage').and.callThrough();
    component.getPage(5);
    // expectations
    expect(pageSpy).toHaveBeenCalledOnceWith(5);
    expect(component.currentPage).toBe(5);
  });

  it('T17.9 should open dataset details view', () => {
    // fake data
    let charts: GeoChart[] = [{
      id: 1, slug: '', designation: '', description: '', chartType: 'BAR',
      series: [{ id: 1, slug: 'slug', name: 'name', color: '#000', points: [] }],
    }];
    component.charts = charts;
    fixture.detectChanges();

    // spies
    let datasetViewSpy = spyOn(component, 'toggleChartView').and.callThrough();

    component.toggleChartView(1);

    // expectations
    expect(datasetViewSpy).toHaveBeenCalledWith(1);
    expect(component.isChartOpen).toBeTrue();
    expect(component.displayedHeaders).toEqual(component.openHeaders);
    expect(component.openChart).toEqual(charts[0]);
    expect(component.chartDataInput).toEqual(charts[0]);
  });

  it('T17.10 should close dataset details view', () => {
    // fake data
    let charts: GeoChart[] = [{
      id: 1, slug: '', designation: '', description: '', chartType: 'BAR',
      series: [{ id: 1, slug: 'slug', name: 'name', color: '#000', points: [] }],
    }];
    component.charts = charts;
    fixture.detectChanges();

    // spies
    let datasetViewSpy = spyOn(component, 'toggleChartView').and.callThrough();

    component.toggleChartView(-1);

    // expectations
    expect(datasetViewSpy).toHaveBeenCalledWith(-1);
    expect(component.isChartOpen).toBeFalse();
    expect(component.displayedHeaders).toEqual(component.headers);
  });

  it('T17.11 it should add series to add dataset form', () => {
    let getSpy = spyOnProperty(component, 'newSeries').and.callThrough();
    let addSpy = spyOn(component, 'addNewSeries').and.callThrough();
    let createSpy = spyOn(component, 'createSeries').and.callThrough();
    let result = component.newSeries;
    component.addNewSeries();
    expect(getSpy).toHaveBeenCalled();
    expect(addSpy).toHaveBeenCalled();
    expect(result).toEqual(<FormArray>component.addChartForm.get('series'));
    expect(createSpy).toHaveBeenCalled();
  });

  it('T17.12 it should get series from add chart form', () => {
    let getSpy = spyOnProperty(component, 'newSeries').and.callThrough();
    let result = component.newSeries;
    expect(getSpy).toHaveBeenCalled();
    expect(result).toEqual(<FormArray>component.addChartForm.get('series'));
  });

  it('T17.13 it should get series from edit chart form', () => {
    let getSpy = spyOnProperty(component, 'editSeries').and.callThrough();
    let result = component.editSeries;
    expect(getSpy).toHaveBeenCalled();
    expect(result).toEqual(<FormArray>component.editChartForm.get('series'));
  });

  describe('TS17.2 create a new chart', () => {
    it('T17.2.1 should not create a new chart if new chart form is invalid', () => {
      // spies
      let createSpy = spyOn(component, 'createNewChart').and.callThrough();
      let addAPISpy = spyOn(component['chartServ'], 'addChart');
      let getInfoSpy = spyOn(component, 'getChartsData');
      let rowSpy = spyOn(component, 'updateRowCount');

      component.createNewChart();

      // expectations
      expect(createSpy).toHaveBeenCalled();
      expect(addAPISpy).not.toHaveBeenCalled();
      expect(getInfoSpy).not.toHaveBeenCalled();
      expect(rowSpy).not.toHaveBeenCalled();
    });

    it('T17.2.2 should create a new chart', () => {
      // spies
      let createSpy = spyOn(component, 'createNewChart').and.callThrough();
      let addAPISpy = spyOn(component['chartServ'], 'addChart').and.returnValue(of({
        id: 1, slug: 'slug', designation: 'design', description: 'desc', chartype: 'BAR',
        series: [{ id: 1, slug: 'slug', name: 'name', color: '#000' }]
      }));
      let getInfoSpy = spyOn(component, 'getChartsData').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new information
      component.addChartForm.patchValue({ slug: 'slug', designation: 'designation', description: 'desc', type: 'BAR' });
      component.newSeries.controls[0].patchValue({ seriesSlug: 'slug', seriesName: 'name', seriesColor: '#000' });
      fixture.detectChanges();

      component.createNewChart();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      expect(getInfoSpy).toHaveBeenCalled();
      expect(rowSpy).toHaveBeenCalled();
      expect(component.charts.length).not.toBe(0)
    });

    it('T17.2.3 should check form controls when creating a new chart', () => {
      // for coverage purposes
      // spies
      let createSpy = spyOn(component, 'createNewChart').and.callThrough();
      let addAPISpy = spyOn(component['chartServ'], 'addChart').and.returnValue(of({
        id: 1, slug: 'slug', designation: 'design', description: 'desc', chartype: 'BAR',
        series: [{ id: 1, slug: 'slug', name: 'name', color: '#000' }]
      }));
      let getInfoSpy = spyOn(component, 'getChartsData').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new information
      component.addChartForm.patchValue({ slug: 'slug', designation: 'designation', description: 'desc', type: 'BAR' });
      component.addChartForm.setControl('series', new FormArray([new FormControl('fake')]));
      fixture.detectChanges();

      component.createNewChart();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      expect(getInfoSpy).toHaveBeenCalled();
      expect(rowSpy).toHaveBeenCalled();
      expect(component.charts.length).not.toBe(0)
    });

    it('T17.2.4 should handle error from creating a new chart', () => {
      // spies
      let createSpy = spyOn(component, 'createNewChart').and.callThrough();
      let addAPISpy = spyOn(component['chartServ'], 'addChart').and.returnValue(throwError(() => new Error()));
      let getInfoSpy = spyOn(component, 'getChartsData').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new information
      component.addChartForm.patchValue({ slug: 'slug', designation: 'designation', description: 'desc', type: 'BAR' });
      component.newSeries.controls[0].patchValue({ seriesSlug: 'slug', seriesName: 'name', seriesColor: '#000' });
      fixture.detectChanges();

      component.createNewChart();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      expect(getInfoSpy).not.toHaveBeenCalled();
      expect(rowSpy).not.toHaveBeenCalled();
      expect(component.charts.length).toBe(0)
    });
  });

  describe('TS17.3 update an existing chart', () => {

    it('T17.3.1 should not update a chart if edit chart form is invalid', () => {
      // spies
      let updateSpy = spyOn(component, 'updateChart').and.callThrough();
      let updateAPISpy = spyOn(component['chartServ'], 'updateChart');

      component.updateChart();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).not.toHaveBeenCalled();
    });

    it('T17.3.2 should update a chart', () => {
      // spies
      let updateSpy = spyOn(component, 'updateChart').and.callThrough();
      let updateAPISpy = spyOn(component['chartServ'], 'updateChart').and.returnValue(of({
        id: 1, slug: 'slug', designation: 'design', description: 'desc', chartype: 'BAR',
        series: [{ id: 1, slug: 'slug', name: 'name', color: '#000' }]
      }));

      // fake edit information
      component.editChartForm.patchValue({ slug: 'slug', designation: 'designation', description: 'desc', type: 'BAR' });
      component.editSeries.push(new FormGroup({
        seriesSlug: new FormControl('slug'),
        seriesName: new FormControl('name'),
        seriesColor: new FormControl('#000'),
      }));
      let openChart: GeoChart = {
        id: 1, slug: 'slug', designation: 'designation', description: 'desc', chartType: 'BAR',
        series: [{ id: 1, slug: 'slug', name: 'name', color: '#000', points: [] }],
      };
      component.openChart = openChart;
      component.editChart = openChart;
      component.charts = [openChart];
      fixture.detectChanges();

      component.updateChart();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateAPISpy).toHaveBeenCalled();
      expect(component.charts.length).not.toBe(0)
    });

    it('T17.3.3 should check form controls when updating a chart', () => {
      // for coverage purposes
      // spies
      let updateSpy = spyOn(component, 'updateChart').and.callThrough();
      let updateAPISpy = spyOn(component['chartServ'], 'updateChart').and.returnValue(of({
        id: 1, slug: 'slug', designation: 'design', description: 'desc', chartype: 'BAR',
        series: [{ id: 1, slug: 'slug', name: 'name', color: '#000' }]
      }));

      // fake edit information
      component.editChartForm.patchValue({ slug: 'slug', designation: 'designation', description: 'desc', type: 'BAR' });
      component.editSeries.push(new FormGroup({ fake: new FormControl('fake') }));
      let openChart: GeoChart = {
        id: 1, slug: 'slug', designation: 'designation', description: 'desc', chartType: 'BAR',
        series: [{ id: 1, slug: 'slug', name: 'name', color: '#000', points: [] }],
      };
      component.openChart = openChart;
      component.editChart = openChart;
      component.charts = [openChart];
      fixture.detectChanges();

      component.updateChart();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateAPISpy).toHaveBeenCalled();
      expect(component.charts.length).not.toBe(0)
    });

    it('T17.3.4 should handle error from updating a chart', () => {
      // spies
      let updateSpy = spyOn(component, 'updateChart').and.callThrough();
      let updateAPISpy = spyOn(component['chartServ'], 'updateChart').and.returnValue(throwError(() => new Error()));

      // fake edit information
      component.editChartForm.patchValue({ slug: 'slug', designation: 'designation', description: 'desc', type: 'BAR' });
      component.editSeries.push(new FormGroup({
        seriesSlug: new FormControl('slug'),
        seriesName: new FormControl('name'),
        seriesColor: new FormControl('#000'),
      }));
      let openChart: GeoChart = {
        id: 1, slug: 'slug', designation: 'designation', description: 'desc', chartType: 'BAR',
        series: [{ id: 1, slug: 'slug', name: 'name', color: '#000', points: [] }],
      };
      component.openChart = openChart;
      component.editChart = openChart;
      component.charts = [openChart];
      fixture.detectChanges();

      component.updateChart();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateAPISpy).toHaveBeenCalled();
      expect(component.charts.length).toBe(1)
    });
  });

  describe('TS17.4 delete an existing chart', () => {
    it('T17.4.1 should not delete chart without confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeChart').and.callThrough();
      let deleteAPISpy = spyOn(component['chartServ'], 'deleteChart');

      component.removeChart();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).not.toHaveBeenCalled();
    });

    it('T17.4.2 should delete chart if there was confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeChart').and.callThrough();
      let deleteAPISpy = spyOn(component['chartServ'], 'deleteChart').and.returnValue(of({}));
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake information
      let charts: GeoChart[] = [{
        id: 1, slug: 'chartSlug', designation: '', description: '', chartType: 'BAR',
        series: [{ id: 1, slug: 'slug', name: 'name', color: '#000', points: [] }],
      }];
      component.charts = charts;
      component.openChart = charts[0];
      component.isConfChecked = true;
      fixture.detectChanges();

      component.removeChart();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).toHaveBeenCalledWith('chartSlug');
      expect(component.charts).toEqual([]);
      expect(component.isChartOpen).toBeFalse();
      expect(component.displayedHeaders).toEqual(component.headers);
      expect(rowSpy).toHaveBeenCalledWith(0);
    });

    it('T17.4.3 should handle error on deleting chart', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeChart').and.callThrough();
      let deleteAPISpy = spyOn(component['chartServ'], 'deleteChart').and.returnValue(throwError(() => new Error()));
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake information
      let charts: GeoChart[] = [{
        id: 1, slug: 'chartSlug', designation: '', description: '', chartType: 'BAR',
        series: [{ id: 1, slug: 'slug', name: 'name', color: '#000', points: [] }],
      }];
      component.charts = charts;
      component.openChart = charts[0];
      component.isConfChecked = true;
      fixture.detectChanges();

      component.removeChart();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).toHaveBeenCalledWith('chartSlug');
      expect(component.charts).toEqual(charts);
      expect(rowSpy).not.toHaveBeenCalled();
    });
  });

});
