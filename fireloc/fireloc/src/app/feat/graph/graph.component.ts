import { Component, Input, OnChanges, OnInit, SimpleChanges, ViewChild } from '@angular/core';

// Interfaces
import { GeoChart } from 'src/app/interfaces/graphs';

// Chart JS
import { ChartDataSets, ChartOptions, ChartType } from 'chart.js';
import { BaseChartDirective, Color, Label } from 'ng2-charts';

/**
 * Graph component.
 * 
 * Displays a ChartJS chart according to the data input. Types of graphs are exclusive to scatter, pie, bar, and line.
 * See {@link GraphsComponent} for usage.
 */
@Component({
  selector: 'feat-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.css']
})
export class GraphComponent implements OnInit, OnChanges {

  /**
   * input data for chart to display
   */
  @Input('chartData') chartDataInput!: GeoChart;

  // Chart JS
  /**
   * reference to the ChartJS chart in the DOM
   */
  @ViewChild(BaseChartDirective) chart!: BaseChartDirective;
  /**
   * chart datasets
   */
  chartData!: ChartDataSets[];        
  /**
   * chart type (bar, line, scatter or pie)
   */
  chartType!: ChartType;              
  /**
   * chart plugins
   */
  chartPlugins = [];                  
  /**
   * chart axis labels
   */
  chartLabels!: Label[];              
  /**
   * chart options
   */
  chartOptions!: ChartOptions;        
  /**
   * chart series colors
   */
  chartColors!: Color[];              

  /**
   * Empty constructor
   */
  constructor() { }

  /**
   * Defines the chart type and initializes the chart data according to the chart type.
   */
  ngOnInit(): void {
    // define chart type
    this.chartType = this.chartDataInput.chartType.toLowerCase() as ChartType;

    // get chart data according to chart type
    switch (this.chartType) {
      case 'scatter':
        this.chartLabels = this.getChartLabels();       // define chart labels
        this.chartOptions = this.getChartOptions();     // define chart options
        this.chartColors = this.getScatterColors();     // define chart colors
        this.chartData = this.getScatterDatasets();     // define chart dataset
        break;
      case 'pie':
        this.chartLabels = this.getPieLabels();         // define chart labels
        this.chartOptions = this.getPieOptions();       // define chart options
        this.chartColors = this.getPieColors();         // define chart colors
        this.chartData = this.getPieDatasets();         // define chart dataset
        break;
      case 'line':
      case 'bar':
        this.chartLabels = this.getChartLabels();       // define chart labels
        this.chartOptions = this.getChartOptions();     // define chart options
        this.chartColors = this.getLineColors();        // define chart colors
        this.chartData = this.getChartDatasets();       // define chart dataset
        break;
    }
  }

  /**
   * Detects changes in the input variables. Only change of importance to note is a change in the chart input data.
   * 
   * When a change is detected in the chart data input, it makes a call to re-render the chart.
   * @param changes changes on inputs
   */
  ngOnChanges(changes: SimpleChanges): void {
    for (let propName in changes) {
      // re-render data
      if (propName === 'chartDataInput') {
        this.ngOnInit();
      }
    }
  }

  // GENERAL METHODS

  /* getChartTitle(): string[] {
    return [this.chartDataInput.designation, this.chartDataInput.description];
  } */

  /**
   * Sets the chart options for a chart. Used by ChartJS in the template.
   * @returns JSON object with chart options
   */
  getChartOptions(): ChartOptions {
    return {
      responsive: true,
      plugins: {
        tooltip: {
          mode: 'point'
        },
      },
      /* title: {
        display: true,
        text: this.getChartTitle()
      }, */
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      },
    };
  }
  /**
   * Sets the chart axis labels. Uses the chart data input to get the proper labels.
   * @returns list of labels
   */
  getChartLabels(): Label[] {
    let labels: Label[] = [];

    this.chartDataInput.series[0].points.forEach((point) => {
      labels.push(point.x.toString());
    });

    return labels;
  }
  /**
   * Prepares the chart datasets to be used by ChartJS with the chart input provided.
   * @returns list of chart datasets
   */
  getChartDatasets(): ChartDataSets[] {
    let chartDataSets: any[] = [];

    this.chartDataInput.series.forEach((series) => {
      let data: any = [];
      // get data from series
      series.points.forEach((point) => data.push(point.y));

      // add dataset to chart
      chartDataSets.push({
        data: data,
        fill: this.chartType !== 'line' ? true : false,
        label: series.name,
        backgroundColor: series.color,
      });
    });

    return chartDataSets as ChartDataSets[];
  }

  // SCATTER METHODS
  /**
   * Prepares the chart datasets to be used by ChartJS with the chart input provided. 
   * Method specific for scatter charts due to specific dataset settings to be declared.
   * @returns list of chart datasets
   */
  getScatterDatasets(): ChartDataSets[] {
    let chartDataSets: any[] = [];

    this.chartDataInput.series.forEach((series) => {
      let data: any = [];
      // get data from series
      series.points.forEach((point) => data.push({ x: point.x, y: point.y }));

      // add dataset to chart
      chartDataSets.push({
        data: data,
        pointRadius: 5,
        label: series.name,
        backgroundColor: series.color,
        pointBackgroundColor: series.color,
      });
    });

    return chartDataSets as ChartDataSets[];
  }
  /**
   * Gets specific colors for the scatter points in a scatter chart.
   * @returns list of scatter series colors
   */
  getScatterColors(): Color[] {
    let colors: Color[] = [];
    this.chartDataInput.series.forEach((s) => {
      colors.push({ borderColor: s.color });
    });
    return colors;
  }

  // PIE METHODS
  /**
   * Prepares the chart datasets to be used by ChartJS with the chart input provided. 
   * Method specific for pie charts due to specific dataset settings to be declared.
   * @returns list of chart datasets
   */
  getPieDatasets(): ChartDataSets[] {
    let chartDataSets: any[] = [];
    let data: any = [];

    this.chartDataInput.series.forEach((series) => {
      // get data from series
      series.points.forEach((point) => data.push(point.y));
    });
    // add dataset to chart
    chartDataSets.push({
      data: data,
    });

    return chartDataSets as ChartDataSets[];
  }
  /**
   * Sets the chart options specific for pie charts.
   * @returns JSON object with chart options
   */
  getPieOptions(): ChartOptions {
    return {
      responsive: true,
      plugins: {
        tooltip: {
          mode: 'point'
        },
      },
      /* title: {
        display: true,
        text: this.getChartTitle()
      }, */
    };
  }
  /**
   * Sets the chart axis labels. Uses the chart data input to get the proper labels for a pie chart.
   * @returns list of labels
   */
  getPieLabels(): Label[] {
    let labels: Label[] = [];
    this.chartDataInput.series.forEach((s) => {
      labels.push(s.name);
    });
    return labels;
  }
  /**
   * Gets specific colors for the pie portions in a pie chart.
   * @returns list of series colors
   */
  getPieColors(): Color[] {
    let colors: any[] = [{ backgroundColor: [] }];
    this.chartDataInput.series.forEach((s) => {
      colors[0].backgroundColor.push(s.color);
    });
    return colors;
  }

  // LINE METHODS
  /**
   * Gets specific colors for the line colors in a line chart.
   * @returns list of series colors
   */
  getLineColors(): Color[] {
    let colors: Color[] = [];
    this.chartDataInput.series.forEach((s) => {
      colors.push({ borderColor: s.color });
    });
    return colors;
  }
}
