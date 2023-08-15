import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

// Style
import {
  faCalendarDay,
  faChevronDown,
  faGlobeAfrica,
  faPencilAlt,
  faSearch,
  faTimes,
  faTrash
} from '@fortawesome/free-solid-svg-icons';
import { NgbDate, NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Constants
import { Extent } from 'src/app/constants/mapext';

// Interfaces
import { TableHeader } from 'src/app/interfaces/backoffice';
import { MapSettings } from 'src/app/interfaces/maps';

// Services
import { MarkerService } from 'src/app/serv/leafmap/marker.service';

/**
 * Backoffice Events component.
 * 
 * Displays a list of FireLoc events. A single event can be viewed, edited or deleted.
 * It is also possible to filter the events with search terms, by location or by time period.
 */
@Component({
  selector: 'boff-events',
  templateUrl: './events.component.html',
  styleUrls: ['./events.component.css']
})
export class EventsComponent implements OnInit {

  // icons
  /**
   * icon for dropdown menus
   */
  dropIcon = faChevronDown;
  /**
   * icon for location
   */
  locIcon = faGlobeAfrica;
  /**
   * icon for dates
   */
  dateIcon = faCalendarDay;
  /**
   * icon for searches
   */
  searchIcon = faSearch;
  /**
   * icon for event edition
   */
  editIcon = faPencilAlt;
  /**
   * icon for event deletion
   */
  deleteIcon = faTrash;
  /**
   * icon to close information
   */
  closeIcon = faTimes;

  // TODO REPLACE WITH API DATA
  /**
   * list of FireLoc events. Currently holds fake data due to API unavailability
   */
  events: any[] = [
    { id: 1, place: 'Lisboa - Santarém', duration: '12/08/2019 - A Decorrer', dim: 'Sem Informação', freg: 'Freg A', mun: 'Mun A' },
    { id: 2, place: 'Lousã - Coimbra', duration: '20/09/2019 - 25/09/2019', dim: '100km', freg: 'Freg B', mun: 'Mun B' },
    { id: 3, place: 'Porto - Bragança', duration: '21/09/2022 - A Decorrer', dim: 'Sem Informação', freg: 'Freg C', mun: 'Mun C' },
    { id: 4, place: 'Soure - Pombal', duration: '28/09/2020 - A Decorrer', dim: 'Sem Informação', freg: 'Freg D', mun: 'Mun D' },
    { id: 5, place: 'Coimbra - Figueira da Foz', duration: '10/05/2020 - A Decorrer', dim: 'Sem Informação', freg: 'Freg E', mun: 'Mun E' },
  ];

  /**
   * list of table headers for table component
   */
  headers: TableHeader[] = [
    { objProperty: 'id', columnLabel: '#' },
    { objProperty: 'place', columnLabel: 'Localização' },
    { objProperty: 'duration', columnLabel: 'Duração' },
    { objProperty: 'dim', columnLabel: 'Dimensão' },
    { objProperty: 'freg', columnLabel: 'Freguesia' },
    { objProperty: 'mun', columnLabel: 'Município' },
  ];
  /**
   * list of headers to be displayed when a single event is closed
   */
  displayedHeaders: TableHeader[] = this.headers;

  /**
   * search terms for data filtering
   */
  searchTerms: string = '';

  // location filter
  /**
   * flag to determine if map for location filtering is visible
   */
  showFilterMap: boolean = false;
  /**
   * reference for location filter map
   */
  filterMap: any = null;
  /**
   * location filter map settings
   */
  filterMapsettings: MapSettings = {
    domElem: "filter-map",
    mapContainer: "filterMap",
    minZoom: 6,
    maxZoom: 20,
    scale: true,
    zoomCtrl: true,
    bounds: Extent.bounds,
    fullext: Extent.maxBounds,
    wfs: [],
    wms: []
  };
  /**
   * feature group for location filter map
   */
  filterPolygroup!: L.FeatureGroup;
  /**
   * number of points in location filter
   */
  pointCounter: number = 0;
  /**
  * list of points with coordinates for location filtering
  */
  filterPoints: any[] = [];

  // date range filter
  /**
   * reference to hovered date
   */
  hoveredDate: NgbDate | null = null;
  /**
   * start date for date filtering
   */
  fromDate: NgbDate | null = null;
  /**
   * end date for date filtering
   */
  toDate: NgbDate | null = null;

  // event details
  /**
   * flag to determine if a single event's information is being displayed 
   */
  isEventOpen: boolean = false;
  /**
   * list of headers to be displayed when a single event is open
   */
  openHeaders: TableHeader[] = this.headers.filter((_, index) => index < 3);
  /**
   * reference to open event
   */
  openEvent: any = {};
  /**
   * determines which event information section is displayed
   */
  selectedEventSection: number = 1;

  // event map
  /**
   * event map settings
   */
  mapsettings: MapSettings = {
    domElem: "event-map",
    mapContainer: "eventMap",
    minZoom: 0,
    maxZoom: 20,
    scale: true,
    zoomCtrl: true,
    bounds: Extent.bounds,
    fullext: Extent.maxBounds,
    wfs: [],
    wms: []
  };
  /**
   * reference for event map
   */
  map: any = null;

  // pagination
  /**
   * current page of data being displayed
   */
  currentPage: number = 1;
  /**
   * number of rows of data in the table
   */
  rowCount: number = this.events.length;

  // edit event
  /**
   * edit event form
   */
  editEventForm!: FormGroup;
  /**
   * reference to open event for editing
   */
  editEvent: any = { name: '', place: '', start: '', end: '', type: '', cause: '', geom: '', codsgif: 0, codncco: 0, }

  // remove event
  /**
  * flag to determine if user has confirmed event removal
  */
  isConfChecked: boolean = false;
  /**
   * flag to determine if user has decided to remove an event
   */
  hasClickedRemove: boolean = false;

  /**
   * Empty constructor for the Backoffice events component.
   * @param markerServ map marker service. See {@link MarkerService}.
   * @param modalService Bootstrap modal service
   */
  constructor(private markerServ: MarkerService, private modalService: NgbModal) { }

  /**
   * Initializes necessary forms (edit an event). Method is incomplete due to API unavailability.
   */
  ngOnInit(): void {
    // TODO CHECK WITH API DOCS
    this.editEventForm = new FormGroup({
      name: new FormControl(this.editEvent.name, [Validators.required]),
      place: new FormControl(this.editEvent.place, [Validators.required,]),
      start: new FormControl(this.editEvent.start, [Validators.required,]),
      end: new FormControl(this.editEvent.end, [Validators.required,]),
      type: new FormControl(this.editEvent.type, [Validators.required]),
      cause: new FormControl(this.editEvent.cause, [Validators.required]),
      geom: new FormControl(this.editEvent.geom, []),
      codSGIF: new FormControl(this.editEvent.codsgif, [Validators.required]),
      codNCCO: new FormControl(this.editEvent.codncco, [Validators.required]),
    });
  }

  /**
   * Updates search terms.
   * Searches events by place, 'Fregusia' and 'Município' in table component. 
   * See {@link TableComponent#filterDataSearchEvents} for more information.
   * @param searchTerms new search terms
   */
  searchEvents(searchTerms: string) {
    // ignore clear search event
    if (typeof (searchTerms) === 'string') this.searchTerms = searchTerms;
  }

  /**
   * Receives map for location filtering. Sets up the onClick method for the map.
   * @param map leaflet map
   */
  receiveFilterMap(map: any) {
    this.filterMap = map;
    this.filterMap.on("click", (e: any) => { this.createPolyline(e.latlng); })
  }

  /**
   * Updates the showFilterMap flag according to location filter map display.
   * @param parentElem DOM element responsible for hiding or showing the map
   */
  toggleFilterMap(parentElem: HTMLDivElement) {
    // if class 'show' is in parent, construct map
    this.showFilterMap = !parentElem.className.includes('show'); // reverse due to post-rendering
    // clear filter points
    if (!this.showFilterMap) {
      this.pointCounter = 0;
      this.filterPoints = [];
    }
  }

  /**
   * Creates polyline in map for location filtering. 
   * If all necessary points for location filtering have been added, it creates a closed polygon for better location filtering visualization.
   * @param coordinates coordinates of the clicked point on the map
   * @returns nothing
   */
  createPolyline(coordinates: any) {
    // initialize line group
    if (this.pointCounter === 0) this.filterPolygroup = this.markerServ.startPolylineGroup(this.filterMap);

    // clear filter if clicked after finishing polygon
    if (this.pointCounter === 4) { this.clearLocFilter(); return; }

    // add point to line
    this.filterPoints.push([
      coordinates.lat,
      coordinates.lng
    ]);
    this.markerServ.addPolylineToFilterMap(this.filterPoints, this.filterPolygroup);

    // finish
    if (this.pointCounter === 3) this.markerServ.addPolygonToFilterMap(this.filterPoints, this.filterPolygroup);

    // increase counter
    this.pointCounter += 1;
  }

  // TODO API REQUEST
  /**
   * Filters events by geographical location. 
   * Method is incomplete due to API unavailability.
   */
  filterLoc() {
    // send to API
  }

  /**
   * Clears the location filter information.
   */
  clearLocFilter() {
    // reset variables
    this.pointCounter = 0;
    this.filterPoints = [];

    // clear map
    this.markerServ.clearPolyGroup(this.filterPolygroup);
  }

  /**
   * Method called upon date selection in Bootstrap Date Picker. 
   * Determines if selected date should be the start date, end date or update the date range.
   * @param date date selected.
   */
  onDateSelection(date: NgbDate) {
    if (!this.fromDate && !this.toDate) this.fromDate = date;
    else if (this.fromDate && !this.toDate && date.after(this.fromDate)) this.toDate = date;
    else {
      this.toDate = null;
      this.fromDate = date;
    }
  }

  /**
   * Method used by the Bootstrap Date Picker. Determines if a date should appear with a hovered state.
   * @param date date to check
   * @returns true if date should have hover, false if otherwise
   */
  isHovered(date: NgbDate) {
    return (
      this.fromDate && !this.toDate && this.hoveredDate && date.after(this.fromDate) && date.before(this.hoveredDate)
    );
  }

  /**
   * Method used by the Bootstrap Date Picker. Checks whether selected date is inside the selected date range.
   * @param date new date to check
   * @returns true if date is inside range, false if otherwise
   */
  isInside(date: NgbDate) { return this.toDate && date.after(this.fromDate) && date.before(this.toDate); }

  /**
   * Method used by the Bootstrap Date Picker. Checks whether selected dates form a date range.
   * @param date new date to check
   * @returns true if dates form a range, false if otherwise
   */
  isRange(date: NgbDate) {
    return (
      date.equals(this.fromDate) ||
      (this.toDate && date.equals(this.toDate)) ||
      this.isInside(date) ||
      this.isHovered(date)
    );
  }

  /**
   * Updates row count of filtered data for pagination
   * @param rows number of rows
   */
  updateRowCount(rows: number) { this.rowCount = rows; }

  /**
   * Updates the current page of displayed data
   * @param page current page
   */
  getPage(page: any) { this.currentPage = page; }

  /**
   * Opens or closes the display of a single event's information details.
   * @param eventID event ID to display or -1 to close information
   */
  toggleEventView(eventID: number) {
    // close event details
    if (eventID === -1) {
      this.isEventOpen = false;
      this.displayedHeaders = this.headers;
    }
    // open event details
    else {
      this.selectedEventSection = 1;
      this.isEventOpen = true;
      this.displayedHeaders = this.openHeaders;

      // find event with selected event ID
      let eventIndex = this.events.findIndex(item => item.id === eventID);
      this.openEvent = this.events[eventIndex];
    }
  }

  /**
   * Selects event section information to be displayed
   * @param sectionID 
   */
  selectEventSection(sectionID: number) { this.selectedEventSection = sectionID; }

  /**
   * Receives map from child map component to display event's location.
   * Method is incomplete due to API unavailability.
   * @param map leaflet map
   */
  receiveMap(map: any) {
    this.map = map;

    // Add contribution Location
    if (this.map !== null) {
      // TODO CHANGE WITH EVENT COORDINATES
      this.markerServ.addMarkerToMap(this.map, 40.185587, -8.415428);
    }
  }

  /**
   * Opens a Bootstrap modal to display content. Method is incomplete due to API unavailability.
   * @param content modal content to display
   */
  open(content: any) {
    // reset variables for new modal
    this.isConfChecked = false;
    this.hasClickedRemove = false;

    // open modal
    this.modalService.open(content, { centered: true, size: 'lg' });
  }

  /**
   * Updates event information from edit input form
   * @param value updated value
   * @param field event property to update
   */
  updateEditEventField(value: string | number, field: string) { this.editEvent[field] = value; }

  // TODO IMPLEMENT WITH API
  /**
   * Updates an event if edit event form is valid.
   * 
   * Method is incomplete due to API unavailability.
   */
  updateEvent() {
    // check if form is valid
    if (this.editEventForm.valid) {
      // ...
    }

    // close and reset
    this.editEventForm.reset();
    this.modalService.dismissAll();
  }

  // TODO COMPLETE WITH API
  /**
   * Checks if the user has confirmed the removal of an event.
   * 
   * If there is confirmation, delete an event with the API and update the displayed data.
   * 
   * Method is incomplete due to API unavailability.
   */
  deleteEvent() {
    this.hasClickedRemove = true;
    // without checked confirmation, show error
    if (this.isConfChecked) {
      // remove event from list
      let eventIndex = this.events.findIndex(item => item.id === this.openEvent.id);
      this.events.splice(eventIndex, 1);

      // update table and pagination
      this.events = JSON.parse(JSON.stringify(this.events));
      this.updateRowCount(this.events.length);

      // ...

      // close and reset
      this.isEventOpen = false;
      this.displayedHeaders = this.headers;
      this.isConfChecked = false;
      this.hasClickedRemove = false;
      this.modalService.dismissAll();
    }
  }
}
