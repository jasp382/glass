import { Component, Input, OnChanges, OnInit, Output, SimpleChanges, EventEmitter } from '@angular/core';

// Fort Awesome
import { faArrowDown, faArrowUp, faTrash, faUserEdit } from '@fortawesome/free-solid-svg-icons';

// Interfaces
import { TableHeader } from 'src/app/interfaces/backoffice';

/**
 * Table component.
 * 
 * Displays a table with provided data. Used in the Backoffice to display list of information obtained with the API.
 */
@Component({
  selector: 'feat-table',
  templateUrl: './table.component.html',
  styleUrls: ['./table.component.css']
})
export class TableComponent implements OnInit, OnChanges {

  /**
   * parent component name
   */
  @Input('component') component: string = '';

  // table data
  /**
   * table dataset
   */
  @Input('data') data!: any[];
  /**
   * table headers
   */
  @Input('headers') headers!: TableHeader[];
  /**
   * emitter for selected row
   */
  @Output('selectedID') selectedIDEmitter: EventEmitter<number> = new EventEmitter<number>();

  // table pagination
  /**
   * current page table
   */
  @Input('page') page: number = 1;
  /**
   * number of rows displayed in one page
   */
  @Input('pageSize') pageSize: number = 10;

  // filtering
  /**
   * filtered data. Data displayed in the table
   */
  filteredData: any[] = [];
  /**
   * emitter for the number of rows currently in the table
   */
  @Output('rowCount') rowCountEmitter: EventEmitter<number> = new EventEmitter<number>();
  /**
   * search terms to filter table data
   */
  @Input('searchFilter') searchFilter: string = '';

  // actions
  /**
   * emitter for selected row for information edition
   */
  @Output('rowEditID') rowEditIDEmitter: EventEmitter<number> = new EventEmitter<number>();
  /**
   * emitter for selected row for information deletion
   */
  @Output('rowDeleteID') rowDeleteIDEmitter: EventEmitter<number> = new EventEmitter<number>();

  /**
   * current selected row
   */
  selectedRowID: number = -1;

  // table sorting
  /**
   * current selected header for sorting
   */
  selectedHeader: number = -1;
  /**
   * current sorting direction (ascending or descending)
   */
  sortDir: string = '';

  // icons
  /**
   * edit icon
   */
  editIcon = faUserEdit;
  /**
   * delete icon
   */
  deleteIcon = faTrash;
  /**
   * down icon
   */
  downArrow = faArrowDown;
  /**
   * up icon
   */
  upArrow = faArrowUp;

  /**
   * Empty constructor
   */
  constructor() { }

  /**
   * Copies data to filtered data to diplay in the table
   */
  ngOnInit(): void {
    // copy data to filtered data array
    this.filteredData = JSON.parse(JSON.stringify(this.data));
  }

  /**
   * Detects changes in the input variables.
   * 
   * If the change is in the search terms, filter the data according to the parent component name.
   * If the change is in the table data, re-render the table and reset the sorting.
   * @param changes 
   */
  ngOnChanges(changes: SimpleChanges): void {
    for (let propName in changes) {

      // if search terms have changed
      if (propName === 'searchFilter') {
        switch (this.component) {
          case 'users':
            // filter user data
            this.filterDataSearchUsers();
            break;
          case 'groups-groups':
            // filter group data
            this.filterDataSearchGroups();
            break;
          case 'contribs':
            // filter contribution data
            this.filterDataSearchContributions();
            break;
          case 'events':
            // filter event data
            this.filterDataSearchEvents();
            break;
          case 'real-events':
            // filter real event data
            this.filterDataSearchRealEvents();
            break;
          case 'graphs':
            // filter graph data
            this.filterDataSearchGraphs();
            break;
          case 'satellite':
            // filter satellite dataset data
            this.filterDataSearchSatellite();
            break;
          case 'raster':
            // filter raster dataset data
            this.filterDataSearchRaster();
            break;
          case 'vector':
            // filter raster dataset data
            this.filterDataSearchVector();
            break;
          default: break;
        }
      }

      // re-render data and reset sorting
      if (propName === 'data') {
        this.filteredData = JSON.parse(JSON.stringify(this.data));

        // reset sorting logic
        this.selectedHeader = -1;
        this.sortDir = '';
      }

    }
  }

  /**
   * Select a row in the table data rows. Does not select a row if clicked on a row icon.
   * 
   * Emits the current selected data ID.
   * @param dataObject row data
   * @param event click or touch event
   * @returns nothing
   */
  selectRow(dataObject: any, event: any) {

    // if row click was on an icon, ignore row select
    if (event.target.tagName === 'svg' || event.target.tagName === 'path')
      return;

    // deselect other rows
    this.filteredData = this.filteredData.map(item => { return { ...item, open: false }; });
    this.data = this.data.map(item => { return { ...item, open: false }; });

    // if new row was selected, update the selected ID 
    if (this.selectedRowID !== dataObject.id) {
      this.selectedRowID = dataObject.id;

      // update data for display
      let objIndex = this.filteredData.findIndex(item => item.id === dataObject.id);
      this.filteredData[objIndex].open = !this.filteredData[objIndex].open;

      // update data for safe keeping
      let dataIndex = this.data.findIndex(item => item.id === dataObject.id);
      this.data[dataIndex].open = !this.data[dataIndex].open;
    }
    // previsously selected row was selected, closing it
    else {
      this.selectedRowID = -1;
    }

    // emit the row ID or -1 if row was closed
    this.selectedIDEmitter.emit(this.selectedRowID);

  }

  /**
   * Sort the table rows by the selected header. 
   * Default sorting starts in descending order which toggles to ascending if same header is selected.
   * @param headerIndex index of the selected header
   */
  sortHeader(headerIndex: number) {
    // if new header selected, sort desc
    if (headerIndex !== this.selectedHeader) {
      this.sortDir = 'desc';
    }
    // same header is selected, toggle sorting directions
    else {
      if (this.sortDir === 'desc') this.sortDir = 'asc';
      else this.sortDir = 'desc';
    }

    // sort data with header
    this.selectedHeader = headerIndex;

    if (this.sortDir === 'asc') {
      this.filteredData = this.filteredData.sort(
        (a, b) =>
          a[this.headers[headerIndex].objProperty] < b[this.headers[headerIndex].objProperty] ?
            1 : a[this.headers[headerIndex].objProperty] > b[this.headers[headerIndex].objProperty] ?
              -1 : 0
      );
    }
    // sortDir === 'desc'
    else {
      this.filteredData = this.filteredData.sort(
        (a, b) =>
          a[this.headers[headerIndex].objProperty] > b[this.headers[headerIndex].objProperty] ?
            1 : a[this.headers[headerIndex].objProperty] < b[this.headers[headerIndex].objProperty] ?
              -1 : 0
      );
    }
  }
 
  /**
   * Filters data with search terms in user column headers
   */
  filterDataSearchUsers() {
    // no filter, skip
    if (this.searchFilter.length === 0)
      this.filteredData = JSON.parse(JSON.stringify(this.data));

    // filter data according to headers -> case insensitive
    else
      this.filteredData = this.data.filter(item =>
        item[this.headers[2].objProperty].toLowerCase().includes(this.searchFilter.toLowerCase()) ||
        item[this.headers[3]?.objProperty]?.toLowerCase().includes(this.searchFilter.toLowerCase()) ||
        item[this.headers[4]?.objProperty]?.toLowerCase().includes(this.searchFilter.toLowerCase())
      );

    // update row count
    this.rowCountEmitter.emit(this.filteredData.length);
  }

  /**
   * Filters data with search terms in groups column headers
   */
  filterDataSearchGroups() {
    // no filter, skip
    if (this.searchFilter.length === 0)
      this.filteredData = JSON.parse(JSON.stringify(this.data));

    // filter data according to headers -> case insensitive
    else
      this.filteredData = this.data.filter(item =>
        item[this.headers[1].objProperty].toLowerCase().includes(this.searchFilter.toLowerCase())
      );

    // update row count
    this.rowCountEmitter.emit(this.filteredData.length);
  }

  /**
   * Filters data with search terms in contributions column headers
   */
  filterDataSearchContributions() {
    // no filter, skip
    if (this.searchFilter.length === 0)
      this.filteredData = JSON.parse(JSON.stringify(this.data));

    // filter data according to headers -> case insensitive
    else
      this.filteredData = this.data.filter(item =>
        item[this.headers[1].objProperty].toLowerCase().includes(this.searchFilter.toLowerCase()) ||
        item[this.headers[3]?.objProperty]?.toLowerCase().includes(this.searchFilter.toLowerCase())
      );

    // update row count
    this.rowCountEmitter.emit(this.filteredData.length);
  }
 
  /**
   * Filters data with search terms in events column headers
   */
  filterDataSearchEvents() {
    // no filter, skip
    if (this.searchFilter.length === 0)
      this.filteredData = JSON.parse(JSON.stringify(this.data));

    // filter data according to headers -> case insensitive
    else
      this.filteredData = this.data.filter(item =>
        item[this.headers[1].objProperty].toLowerCase().includes(this.searchFilter.toLowerCase()) ||
        item[this.headers[4]?.objProperty]?.toLowerCase().includes(this.searchFilter.toLowerCase()) ||
        item[this.headers[5]?.objProperty]?.toLowerCase().includes(this.searchFilter.toLowerCase())
      );

    // update row count
    this.rowCountEmitter.emit(this.filteredData.length);
  }

  /**
   * Filters data with search terms in events column headers
   */
  filterDataSearchRealEvents() {
    // no filter, skip
    if (this.searchFilter.length === 0)
      this.filteredData = JSON.parse(JSON.stringify(this.data));

    // filter data according to headers -> case insensitive
    else
      this.filteredData = this.data.filter(item =>
        item[this.headers[1].objProperty]?.toLowerCase().includes(this.searchFilter.toLowerCase()) ||
        item[this.headers[2].objProperty]?.toLowerCase().includes(this.searchFilter.toLowerCase())
      );

    // update row count
    this.rowCountEmitter.emit(this.filteredData.length);
  }

  /**
   * Filters data with search terms in charts column headers
   */
  filterDataSearchGraphs() {
    // no filter, skip
    if (this.searchFilter.length === 0)
      this.filteredData = JSON.parse(JSON.stringify(this.data));

    // filter data according to headers -> case insensitive
    else
      this.filteredData = this.data.filter(item =>
        item[this.headers[2].objProperty].toLowerCase().includes(this.searchFilter.toLowerCase()) ||
        item[this.headers[3]?.objProperty]?.toLowerCase().includes(this.searchFilter.toLowerCase())
      );

    // update row count
    this.rowCountEmitter.emit(this.filteredData.length);
  }

  /**
   * Filters data with search terms in satellite datasets column headers
   */
  filterDataSearchSatellite() {
    // no filter, skip
    if (this.searchFilter.length === 0)
      this.filteredData = JSON.parse(JSON.stringify(this.data));

    // filter data according to headers -> case insensitive
    else
      this.filteredData = this.data.filter(item =>
        item[this.headers[1].objProperty].toLowerCase().includes(this.searchFilter.toLowerCase()) ||
        item[this.headers[2]?.objProperty]?.toLowerCase().includes(this.searchFilter.toLowerCase())
      );

    // update row count
    this.rowCountEmitter.emit(this.filteredData.length);
  }

  /**
   * Filters data with search terms in raster datasets column headers
   */
  filterDataSearchRaster() {
    // no filter, skip
    if (this.searchFilter.length === 0)
      this.filteredData = JSON.parse(JSON.stringify(this.data));

    // filter data according to headers -> case insensitive
    else
      this.filteredData = this.data.filter(item =>
        item[this.headers[1].objProperty].toLowerCase().includes(this.searchFilter.toLowerCase()) ||
        item[this.headers[2].objProperty].toLowerCase().includes(this.searchFilter.toLowerCase())
      );

    // update row count
    this.rowCountEmitter.emit(this.filteredData.length);
  }

  /**
   * Filters data with search terms in vector datasets column headers
   */
  filterDataSearchVector() {
    // no filter, skip
    if (this.searchFilter.length === 0)
      this.filteredData = JSON.parse(JSON.stringify(this.data));

    // filter data according to headers -> case insensitive
    else
      this.filteredData = this.data.filter(item =>
        item[this.headers[1].objProperty].toLowerCase().includes(this.searchFilter.toLowerCase()) ||
        item[this.headers[2].objProperty].toLowerCase().includes(this.searchFilter.toLowerCase())
      );

    // update row count
    this.rowCountEmitter.emit(this.filteredData.length);
  }

  /**
   * Emits selected object ID for editing
   * @param object selected data 
   */
  editRow(object: any) { this.rowEditIDEmitter.emit(object.id); }

  /**
   * Emits selected object ID for removal
   * @param object selected data 
   */
  deleteRow(object: any) { this.rowDeleteIDEmitter.emit(object.id); }
}
