import { Component, OnInit } from '@angular/core';
import { FormGroup, Validators, FormBuilder, FormArray } from '@angular/forms';

// Font Awesome
import { faChevronDown, faEdit, faFilter, faPlus, faTimes, faTrash } from '@fortawesome/free-solid-svg-icons';

// Bootstrap
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces
import { GeoChart, GeoChartSeries } from 'src/app/interfaces/graphs';
import { TableHeader } from 'src/app/interfaces/backoffice';

// Services
import { ChartService } from 'src/app/serv/rest/chart.service';

/**
 * Backoffice Graphs/Charts component.
 * 
 * Displays a list of FireLoc charts. A single chart can be created, viewed, edited or deleted.
 * It is also possible to filter the chart list with search terms or by chart type.
 */
@Component({
  selector: 'boff-graphs',
  templateUrl: './graphs.component.html',
  styleUrls: ['./graphs.component.css']
})
export class GraphsComponent implements OnInit {

  // icons
  /**
   * icon for type filtering
   */
  typeIcon = faFilter;
  /**
   * drop icon for dropdown menu
   */
  dropIcon = faChevronDown;
  /**
   * plus icon for chart addition
   */
  plusIcon = faPlus;
  /**
   * edit icon for chart edition
   */
  editIcon = faEdit;
  /**
   * delete icon for chart deletion
   */
  deleteIcon = faTrash;
  /**
   * close icon to close information
   */
  closeIcon = faTimes;

  /**
   * list of FireLoc chart datasets
   */
  charts: GeoChart[] = [];

  // chart search
  /**
   * list of available chart types
   */
  types: any[] = [
    { id: 1, name: 'BAR', selected: false }, { id: 2, name: 'LINE', selected: false },
    { id: 3, name: 'PIE', selected: false }, { id: 4, name: 'SCATTER', selected: false },
  ];
  /**
   * list of filtered charts
   */
  filteredCharts: GeoChart[] = [];
  /**
   * list of selected chart types for data filtering
   */
  selectedTypes: string[] = [];
  /**
   * search terms for data filtering
   */
  searchTerms: string = '';

  /**
   * list of table headers for table component
   */
  headers: TableHeader[] = [
    { objProperty: 'id', columnLabel: '#' }, { objProperty: 'chartType', columnLabel: 'Tipo' },
    { objProperty: 'designation', columnLabel: 'Título' }, { objProperty: 'description', columnLabel: 'Descrição' },
  ];

  /**
   * current page of data being displayed
   */
  currentPage: number = 1;
  /**
   * number of rows of data in the table
   */
  rowCount: number = this.charts.length;

  // chart details
  /**
   * flag to determine if a single chart's information is being diplayed
   */
  isChartOpen: boolean = false;
  /**
   * reference to the opened chart's information
   */
  openChart!: GeoChart;
  /**
   * list of table headers to be displayed when no chart is open
   */
  displayedHeaders: TableHeader[] = this.headers;
  /**
   * list of table headers to be displayed when a chart is open
   */
  openHeaders: TableHeader[] = this.headers.filter((_, index) => index < 3);
  /**
   * chart dataset to update ChartJS chart when a single chart's information is being displayed
   */
  chartDataInput!: GeoChart;

  // add chart
  /**
   * new chart form reference
   */
  addChartForm!: FormGroup;
  /**
   * chart type for new chart
   */
  newChartType: string = '';

  // edit chart
  /**
   * edit chart form reference
   */
  editChartForm!: FormGroup;
  /**
   * information of opened chart to update edit chart form values
   */
  editChart: GeoChart = { ...this.openChart };

  // remove chart
  /**
   * flag to determine if user has confirmed chart removal
   */
  isConfChecked: boolean = false;
  /**
   * flag to determine if user has decided to remove a chart
   */
  hasClickedRemove: boolean = false;

  /**
   * Empty constructor for the Backoffice charts component.
   * @param chartServ chart service. See {@link ChartService}.
   * @param modalService Bootstrap modal service
   * @param fb Angular form builder
   */
  constructor(
    private chartServ: ChartService,
    private modalService: NgbModal,
    private fb: FormBuilder
  ) { }

  /**
   * Initializes data and necessary forms (create and edit a chart).
   */
  ngOnInit(): void {
    // get data
    this.getCharts();

    // add data form
    this.addChartForm = this.fb.group({
      slug: ['', [Validators.required, Validators.maxLength(10)]],
      designation: ['', [Validators.required, Validators.maxLength(30)]],
      description: ['', [Validators.required, Validators.maxLength(250)]],
      type: [this.newChartType, [Validators.required,]],
      series: this.fb.array([this.createSeries()], Validators.required),
    });

    // update data form
    this.editChartForm = this.fb.group({
      slug: ['', [Validators.required, Validators.maxLength(10)]],
      designation: ['', [Validators.required, Validators.maxLength(30)]],
      description: ['', [Validators.required, Validators.maxLength(250)]],
      type: ['', [Validators.required,]],
      series: this.fb.array([], Validators.required),
    });
  }

  /**
   * Get charts information from API.
   */
  getCharts() {
    this.chartServ.getCharts().subscribe(
      (result: any) => {
        this.getChartsData(result.data);

        // update values for table and pagination
        this.filteredCharts = JSON.parse(JSON.stringify(this.charts));
        this.updateRowCount(this.filteredCharts.length);
      }, error => { }
    );
  }

  /**
   * Gets chart data from API request response
   * @param rawData API response data
   */
  getChartsData(rawData: any[]) {
    rawData.forEach(c => {
      let newChart: GeoChart = {
        id: c.id,
        slug: c.slug,
        designation: c.designation,
        description: c.description,
        chartType: c.chartype,
        series: this.getSeriesData(c.series),
      }
      this.charts.push(newChart);
    });
  }

  /**
   * Gets series data for chart from API response
   * @param rawData API response data
   * @returns list of chart series
   */
  getSeriesData(rawData: any[]): GeoChartSeries[] {
    let series: GeoChartSeries[] = [];
    rawData.forEach(s => {
      let newSeries: GeoChartSeries = {
        id: s.id,
        slug: s.slug,
        name: s.name,
        color: s.color,
        points: []
      }
      series.push(newSeries);
    })
    return series;
  }

  /**
   * Updates chart search terms. 
   * Searches charts by designation and description in table component.
   * See {@link TableComponent#filterDataSearchGraphs} for more information.
   * @param searchTerms new search terms
   */
  searchCharts(searchTerms: string) {
    // ignore clear search event
    if (typeof (searchTerms) === 'string') {
      this.searchTerms = searchTerms;
    }
  }

  /**
   * Selects chart type to filter chart data
   * @param typeID selected chart type ID
   */
  selectType(typeID: number) {
    let index = this.types.findIndex(t => { return t.id === typeID });
    this.types[index].selected = !this.types[index].selected;

    // get selected types for filtering
    this.selectedTypes = this.types.filter(type => type.selected).map(type => type.name);

    // update data and pagination
    if (this.selectedTypes.length === 0)
      this.filteredCharts = JSON.parse(JSON.stringify(this.charts));
    else
      this.filteredCharts = this.charts.filter(chart => this.selectedTypes.includes(chart.chartType));
    this.updateRowCount(this.filteredCharts.length);
  }

  /**
   * Opens modals to create, update or delete a chart. Initializes the necessary data before opening a modal.
   * @param content modal content to display
   * @param modalType type of modal to open. Can be 'new', 'edit' or 'delete'
   */
  open(content: any, modalType: string) {
    // initialize according to modal
    switch (modalType) {
      case 'new':
        // initialize values
        this.addChartForm.setControl('series', this.fb.array([this.createSeries()], Validators.required));
        this.newChartType = this.types[0].name;
        this.addChartForm.patchValue({ type: this.newChartType });
        break;
      case 'edit':
        // initialize values
        this.editChartForm.setControl('series', this.fb.array([], Validators.required));
        this.initEditChart();
        break;
      case 'delete':
        // reset variables for new modal
        this.isConfChecked = false;
        this.hasClickedRemove = false;
        break;
    }

    // open modal
    this.modalService.open(content, { centered: true, size: 'lg' });
  }

  /**
   * Initializes edit chart information
   */
  initEditChart() {
    // initialize required values in variable
    this.editChart = { ...this.openChart };

    // initialize required values in form control
    this.editChartForm.controls['slug'].setValue(this.editChart.slug);
    this.editChartForm.controls['designation'].setValue(this.editChart.designation);
    this.editChartForm.controls['description'].setValue(this.editChart.description);
    this.editChartForm.controls['type'].setValue(this.editChart.chartType);

    // initialize series
    for (let index = 0; index < this.editChart.series.length; index++) {
      this.editSeries.push(this.createSeries());

      // set initial value in form
      let control = this.editSeries.controls[index];
      control.setValue({
        seriesSlug: this.editChart.series[index].slug,
        seriesName: this.editChart.series[index].name,
        seriesColor: this.editChart.series[index].color,
      });
    };
  }

  /**
   * Updates the filtered data row count. Used for data pagination.
   * @param rows 
   */
  updateRowCount(rows: number) { this.rowCount = rows; }

  /**
   * Updates the current page for data table
   * @param page current page
   */
  getPage(page: any) { this.currentPage = page; }

  /**
   * Opens or closes a chart's information to be displayed.
   * @param chartID chart ID to open or close
   */
  toggleChartView(chartID: number) {
    // close chart details
    if (chartID === -1) {
      this.isChartOpen = false;
      this.displayedHeaders = this.headers;
    }
    // open chart details
    else {
      this.isChartOpen = true;
      this.displayedHeaders = this.openHeaders;

      // find chart with selected chart ID
      let chartIndex = this.charts.findIndex(item => item.id === chartID);
      this.openChart = this.charts[chartIndex];

      // update chart
      this.chartDataInput = JSON.parse(JSON.stringify(this.openChart));
    }
  }

  /**
   * Creates series form group with appropriate form controls and validators.
   * @returns 
   */
  createSeries(): FormGroup {
    return this.fb.group({
      seriesSlug: [null, [Validators.required, Validators.maxLength(10)]],
      seriesName: [null, [Validators.required, Validators.maxLength(50)]],
      seriesColor: ['#000', [Validators.required, Validators.maxLength(7)]],
    });
  }

  /**
   * Pushes new series form group to series form array from add chart form
   */
  addNewSeries() { this.newSeries.push(this.createSeries()); }

  /**
   * Gets series form array from add chart form
   */
  get newSeries(): FormArray { return <FormArray>this.addChartForm.get('series'); }

  /**
   * Gets series form array from edit chart form
   */
  get editSeries(): FormArray { return <FormArray>this.editChartForm.get('series'); }

  /**
   * Checks if the add form is valid.
   * Creates a new chart dataset with the API.
   */
  createNewChart() {
    if (this.addChartForm.valid) {
      // get new chart data values
      let newChartData: any = {
        slug: this.addChartForm.controls.slug.value,
        designation: this.addChartForm.controls.designation.value,
        description: this.addChartForm.controls.description.value,
        chartype: this.newChartType,
        serieslugs: [],
        seriesnames: [],
        seriescolors: [],
      };

      // get new chart series values
      for (let index = 0; index < this.newSeries.controls.length; index++) {
        let control = this.newSeries.controls[index];
        newChartData.serieslugs.push(control.get('seriesSlug')?.value);
        newChartData.seriesnames.push(control.get('seriesName')?.value);
        newChartData.seriescolors.push(control.get('seriesColor')?.value);
      }

      // add new chart with API
      this.chartServ.addChart(newChartData).subscribe(
        (result: any) => {
          this.getChartsData([result]);

          // update values for table and pagination
          this.filteredCharts = JSON.parse(JSON.stringify(this.charts));
          this.updateRowCount(this.filteredCharts.length);
        }, error => { }
      );
    }

    // close and reset
    this.modalService.dismissAll();
    this.addChartForm.reset();
  }

  /**
   * Checks if the edit form is valid.
   * Updates the chart information with the API.
   */
  updateChart() {
    if (this.editChartForm.valid) {
      // get updated data values
      let updatedChartData: any = {
        slug: this.editChartForm.controls.slug.value,
        designation: this.editChartForm.controls.designation.value,
        description: this.editChartForm.controls.description.value,
        chartype: this.editChart.chartType,
        serieslugs: [],
        seriesnames: [],
        seriescolors: [],
      };

      // get updated series values
      for (let index = 0; index < this.editSeries.controls.length; index++) {
        let control = this.editSeries.controls[index];
        updatedChartData.serieslugs.push(this.editChart.series[index].slug); // not possible to edit series slugs
        updatedChartData.seriesnames.push(control.get('seriesName')?.value);
        updatedChartData.seriescolors.push(control.get('seriesColor')?.value);
      }

      // update chart with API
      this.chartServ.updateChart(this.openChart.slug, updatedChartData).subscribe(
        (result: any) => {
          // update in frontend
          this.openChart.slug = result.slug;
          this.openChart.chartType = result.chartype;
          this.openChart.description = result.description;
          this.openChart.designation = result.designation;
          this.openChart.series = this.getSeriesData(result.series);

          // update chart
          this.chartDataInput = JSON.parse(JSON.stringify(this.openChart));

          // update table
          this.filteredCharts = JSON.parse(JSON.stringify(this.charts));
        }, error => { }
      );
    }

    // close and reset
    this.modalService.dismissAll();
    this.editChartForm.reset();
  }

  /**
   * Checks if the user has confirmed the removal of a chart dataset.
   * 
   * If there is confirmation, delete a chart with the API and update the displayed data.
   */
  removeChart() {
    this.hasClickedRemove = true;
    // without checked confirmation, show error
    if (this.isConfChecked) {
      // remove chart with API
      this.chartServ.deleteChart(this.openChart.slug).subscribe(
        (result: any) => {
          // close chart display
          this.isChartOpen = false;
          this.displayedHeaders = this.headers;

          // remove chart from list
          let chartIndex = this.charts.findIndex(item => item.id === this.openChart.id);
          this.charts.splice(chartIndex, 1);

          // update users table and pagination
          this.filteredCharts = JSON.parse(JSON.stringify(this.charts));
          this.updateRowCount(this.filteredCharts.length);
        }, error => { }
      );

      // close
      this.modalService.dismissAll();
    }
  }

}
