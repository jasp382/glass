import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChartsModule } from 'ng2-charts';
import { GeoChart } from 'src/app/interfaces/graphs';
import { SimpleChange, SimpleChanges } from '@angular/core'

// Components
import { GraphComponent } from './graph.component';

function getChartDataBar(): GeoChart {
  let chart: GeoChart = {
    id: 1,
    slug: 'chart',
    designation: 'Bar Chart Title',
    description: 'Bar Chart Description',
    chartType: 'BAR',
    userGroupID: 1,
    series: [
      {
        id: 2,
        slug: 'seriesA',
        name: 'Series A',
        color: '#EE6112',
        points: [
          { x: 1, y: 20 },
          { x: 2, y: 30 },
        ]
      },
      {
        id: 3,
        slug: 'seriesB',
        name: 'Series B',
        color: '#ee1174',
        points: [
          { x: 1, y: 50 },
          { x: 2, y: 10 },
        ]
      },
    ]
  };
  return chart;
}
function getChartDataLine(): GeoChart {
  let chart: GeoChart = {
    id: 1,
    slug: 'chart',
    designation: 'Line Chart Title',
    description: 'Line Chart Description',
    chartType: 'LINE',
    userGroupID: 1,
    series: [
      {
        id: 2,
        slug: 'seriesA',
        name: 'Series A',
        color: '#EE6112',
        points: [
          { x: 1, y: 20 },
          { x: 2, y: 30 },
        ]
      },
      {
        id: 3,
        slug: 'seriesB',
        name: 'Series B',
        color: '#ee1174',
        points: [
          { x: 1, y: 50 },
          { x: 2, y: 10 },
        ]
      },
    ]
  };
  return chart;
}
function getChartDataPie(): GeoChart {
  let chart: GeoChart = {
    id: 1,
    slug: 'chart',
    designation: 'Pie Chart Title',
    description: 'Pie Chart Description',
    chartType: 'PIE',
    userGroupID: 1,
    series: [
      {
        id: 2,
        slug: 'seriesA',
        name: 'Series A',
        color: '#EE6112',
        points: [
          { x: 1, y: 20 },
        ]
      },
      {
        id: 3,
        slug: 'seriesB',
        name: 'Series B',
        color: '#ee1174',
        points: [
          { x: 1, y: 50 },
        ]
      },
    ]
  };
  return chart;
}
function getChartDataScatter(): GeoChart {
  let chart: GeoChart = {
    id: 1,
    slug: 'chart',
    designation: 'Scatter Chart Title',
    description: 'Scatter Chart Description',
    chartType: 'SCATTER',
    userGroupID: 1,
    series: [
      {
        id: 2,
        slug: 'seriesA',
        name: 'Series A',
        color: '#EE6112',
        points: [
          { x: 1, y: 20 },
          { x: 2, y: 30 },
        ]
      },
      {
        id: 3,
        slug: 'seriesB',
        name: 'Series B',
        color: '#ee1174',
        points: [
          { x: 1, y: 50 },
          { x: 2, y: 10 },
        ]
      },
    ]
  };
  return chart;
}

describe('TS28 GraphComponent', () => {
  let component: GraphComponent;
  let fixture: ComponentFixture<GraphComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        GraphComponent,
      ],
      imports: [
        ChartsModule
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(GraphComponent);
    component = fixture.componentInstance;
  });

  it('T28.1 should create', () => {
    expect(component).toBeTruthy();
  });

  it('T28.2 should call correct methods according to chart type (BAR)', () => {
    // fake data
    component.chartDataInput = getChartDataBar();
    fixture.detectChanges();

    // setup spies
    let labelSpy = spyOn(component, 'getChartLabels').and.callThrough();
    let optionsSpy = spyOn(component, 'getChartOptions').and.callThrough();
    let colorSpy = spyOn(component, 'getLineColors').and.callThrough();
    let dataSpy = spyOn(component, 'getChartDatasets').and.callThrough();

    // call ngOnInit
    component.ngOnInit();

    // expectations
    expect(component.chartType).toBe('bar');
    expect(labelSpy).toHaveBeenCalledOnceWith();
    expect(optionsSpy).toHaveBeenCalledOnceWith();
    expect(colorSpy).toHaveBeenCalledOnceWith();
    expect(dataSpy).toHaveBeenCalledOnceWith();
  });

  it('T28.3 should call correct methods according to chart type (LINE)', () => {
    // fake data
    component.chartDataInput = getChartDataLine();
    fixture.detectChanges();

    // setup spies
    let labelSpy = spyOn(component, 'getChartLabels').and.callThrough();
    let optionsSpy = spyOn(component, 'getChartOptions').and.callThrough();
    let colorSpy = spyOn(component, 'getLineColors').and.callThrough();
    let dataSpy = spyOn(component, 'getChartDatasets').and.callThrough();

    // call ngOnInit
    component.ngOnInit();

    // expectations
    expect(component.chartType).toBe('line');
    expect(labelSpy).toHaveBeenCalledOnceWith();
    expect(optionsSpy).toHaveBeenCalledOnceWith();
    expect(colorSpy).toHaveBeenCalledOnceWith();
    expect(dataSpy).toHaveBeenCalledOnceWith();
  });

  it('T28.4 should call correct methods according to chart type (PIE)', () => {
    // fake data
    component.chartDataInput = getChartDataPie();
    fixture.detectChanges();

    // setup spies
    let labelSpy = spyOn(component, 'getPieLabels').and.callThrough();
    let optionsSpy = spyOn(component, 'getPieOptions').and.callThrough();
    let colorSpy = spyOn(component, 'getPieColors').and.callThrough();
    let dataSpy = spyOn(component, 'getPieDatasets').and.callThrough();

    // call ngOnInit
    component.ngOnInit();

    // expectations
    expect(component.chartType).toBe('pie');
    expect(labelSpy).toHaveBeenCalledOnceWith();
    expect(optionsSpy).toHaveBeenCalledOnceWith();
    expect(colorSpy).toHaveBeenCalledOnceWith();
    expect(dataSpy).toHaveBeenCalledOnceWith();
  });

  it('T28.5 should call correct methods according to chart type (SCATTER)', () => {
    // fake data
    component.chartDataInput = getChartDataScatter();
    fixture.detectChanges();

    // setup spies
    let labelSpy = spyOn(component, 'getChartLabels').and.callThrough();
    let optionsSpy = spyOn(component, 'getChartOptions').and.callThrough();
    let colorSpy = spyOn(component, 'getScatterColors').and.callThrough();
    let dataSpy = spyOn(component, 'getScatterDatasets').and.callThrough();

    // call ngOnInit
    component.ngOnInit();

    // expectations
    expect(component.chartType).toBe('scatter');
    expect(labelSpy).toHaveBeenCalledOnceWith();
    expect(optionsSpy).toHaveBeenCalledOnceWith();
    expect(colorSpy).toHaveBeenCalledOnceWith();
    expect(dataSpy).toHaveBeenCalledOnceWith();
  });

  it('T28.6 should call #ngOnInit when chart data input is changed', () => {
    // fake data
    let change: SimpleChanges = { chartDataInput: new SimpleChange(null, getChartDataBar(), true) };
    let ignoredChange: SimpleChanges = { other: new SimpleChange(null, getChartDataBar(), true) };

    // setup spies
    let changesSpy = spyOn(component, 'ngOnChanges').and.callThrough();
    let initSpy = spyOn(component, 'ngOnInit');

    component.ngOnChanges(change);
    component.ngOnChanges(ignoredChange);

    // expectations
    expect(changesSpy).toHaveBeenCalled();
    expect(initSpy).toHaveBeenCalledOnceWith();
  });

});
