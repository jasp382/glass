import { Component, OnInit } from '@angular/core';
import {
  faChevronDown,
  faGlobeAfrica,
  faCalendarDay,
  faPencilAlt,
  faTrash,
  faTimes,
  faChevronUp,
  faInfoCircle,
  faMapMarkerAlt,
  faPlus
} from '@fortawesome/free-solid-svg-icons';
import { NgbDate, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FormControl, FormGroup, Validators } from '@angular/forms';

// Interfaces & Constants
import { TableHeader } from 'src/app/interfaces/backoffice';
import { RealEvent } from 'src/app/interfaces/events';
import { Freg, Mun } from 'src/app/interfaces/georef';
import { FirelocLayer } from 'src/app/interfaces/layers';
import { MapSettings } from 'src/app/interfaces/maps';
import { Extent } from 'src/app/constants/mapext';

// Services
import { RealEventService } from 'src/app/serv/rest/real-event.service';
import { MarkerService } from 'src/app/serv/leafmap/marker.service';

// Other
import { datetimeToRequestString, pointsToWKTF } from 'src/app/util/formatter';

/**
 * Backoffice Real Events component.
 * 
 * Displays a list of real fire events. A single fire event can be created, viewed, updated or deleted.
 * It is also possible to filter the events with search terms, by location or by time period.
 */
@Component({
  selector: 'boff-real-events',
  templateUrl: './real-events.component.html',
  styleUrls: ['./real-events.component.css']
})
export class RealEventsComponent implements OnInit {

  // icons
  /**
   * icon for dropdown menus
   */
  dropIcon = faChevronDown;
  /**
   * @ignore
   */
  upIcon = faChevronUp;
  /**
   * icon for location filter
   */
  locIcon = faGlobeAfrica;
  /**
   * icon for real event creation
   */
  plusIcon = faPlus;
  /**
   * icon for map display
   */
  mapIcon = faMapMarkerAlt;
  /**
   * icon for information
   */
  infoIcon = faInfoCircle;
  /**
   * icon for dates
   */
  dateIcon = faCalendarDay;
  /**
   * icon for real event edition
   */
  editIcon = faPencilAlt;
  /**
   * icon for real event deletion
   */
  deleteIcon = faTrash;
  /**
   * icon to close information
   */
  closeIcon = faTimes;

  /**
   * list of real events
   */
  events: RealEvent[] = [];

  /**
   * search terms for data filtering
   */
  searchTerms: string = '';

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
    domElem: "filter-map-real",
    mapContainer: "filterMapReal",
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

  /**
   * list of table headers for table component
   */
  headers: TableHeader[] = [
    { objProperty: 'id', columnLabel: '#' },
    { objProperty: 'name', columnLabel: 'Nome' },
    { objProperty: 'type', columnLabel: 'Tipo' },
    { objProperty: 'startTime', columnLabel: 'Início' },
    { objProperty: 'endTime', columnLabel: 'Fim' },
  ];

  // Event details
  /**
   * flag to determine if a single real event's information is being displayed 
   */
  isEventOpen: boolean = false;
  /**
   * reference to open real event
   */
  openEvent!: RealEvent;
  /**
   * list of headers to be displayed when a single real event is closed
   */
  displayedHeaders: TableHeader[] = this.headers;
  /**
   * list of headers to be displayed when a single real event is open
   */
  openHeaders: TableHeader[] = this.headers.filter((_, index) => index < 3);
  /**
   * flag to determine if real event map is visible
   */
  isMapVisible: boolean = false;

  // event map
  /**
   * event map settings
   */
  mapsettings: MapSettings = {
    domElem: "real-event-map",
    mapContainer: "realEventMap",
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

  /**
   * new real event form
   */
  newEventForm!: FormGroup;

  /**
   * edit real event form
   */
  editEventForm!: FormGroup;

  // remove a real event
  /**
  * flag to determine if user has confirmed real event removal
  */
  isConfChecked: boolean = false;
  /**
   * flag to determine if user has decided to remove a real event
   */
  hasClickedRemove: boolean = false;

  /**
   * Empty constructor for the Backoffice real events component.
   * @param eventServ real event service. See {@link RealEventService}.
   * @param markerServ map marker service. See {@link MarkerService}.
   * @param modalService Bootstrap modal service
   */
  constructor(private eventServ: RealEventService, private markerServ: MarkerService, private modalService: NgbModal) { }

  /**
   * Initializes data and necessary forms (create and edit a real event).
   */
  ngOnInit(): void {
    // get data
    this.getRealEvents();

    // new event form
    this.newEventForm = new FormGroup({
      // required
      start: new FormControl(null, [Validators.required]),
      end: new FormControl(null, [Validators.required]),
      geom: new FormControl('', [Validators.required]),
      epsg: new FormControl(null, [Validators.required]),
      timezone: new FormControl('', [Validators.required]),
      // optional
      name: new FormControl('', [Validators.maxLength(100)]),
      cause: new FormControl('', [Validators.maxLength(50)]),
      type: new FormControl('', [Validators.maxLength(50)]),
      codSGIF: new FormControl('', [Validators.maxLength(50)]),
      codNCCO: new FormControl('', [Validators.maxLength(50)]),
    });

    // edit event form
    this.editEventForm = new FormGroup({
      // required
      start: new FormControl(null, [Validators.required]),
      end: new FormControl(null, [Validators.required]),
      timezone: new FormControl('', [Validators.required]),
      // optional
      name: new FormControl('', [Validators.maxLength(100)]),
      cause: new FormControl('', [Validators.maxLength(50)]),
      type: new FormControl('', [Validators.maxLength(50)]),
      codSGIF: new FormControl('', [Validators.maxLength(50)]),
      codNCCO: new FormControl('', [Validators.maxLength(50)]),
    });

  }

  /**
   * Updates search terms.
   * Searches real events by name and type in table component. 
   * See {@link TableComponent#filterDataSearchRealEvents} for more information.
   * @param searchTerms new search terms
   */
  searchRealEvents(searchTerms: string) {
    // ignore clear search event
    if (typeof (searchTerms) === 'string') this.searchTerms = searchTerms;
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
   * Gets real fire events from API and updates the displayed data
   */
  getRealEvents() {
    this.eventServ.getRealEventsToken().subscribe(
      (result: any) => {
        this.getEventData(result.data);

        // update values for table and pagination
        this.events = JSON.parse(JSON.stringify(this.events));
        this.updateRowCount(this.events.length);
      }, error => { }
    );
  }

  /**
   * Gets real event data from API response
   * @param rawData API response data
   */
  getEventData(rawData: any[]) {
    rawData.forEach(e => {
      let newEvent: RealEvent = {
        id: e.id,
        name: e.name,
        type: e.tipo,
        startTime: e.start,
        endTime: e.end,
        geom: e.geom,
        cause: e.causa,
        codSGIF: e.codsgif,
        codNCCO: e.codncco,
        burnedArea: e.burnedarea,
        fireLayers: e.firelyr !== undefined ? this.getFireLayers(e.firelyr) : [],
        freg: e.freg !== undefined ? this.getFreg(e.freg) : null,
        mun: e.mun !== undefined ? this.getMun(e.mun) : null,
      };
      this.events.push(newEvent);
    });
  }

  /**
   * Gets parish from API response
   * @param rawData API response data
   * @returns parish if it exists or null
   */
  getFreg(rawData: any[]): Freg | null {
    if (rawData != null) {
      let freg: Freg = {
        id: rawData[0].fid,
        code: rawData[0].code,
        name: rawData[0].name,
        munid: rawData[0].munid,
      }
      return freg;
    }
    return null;
  }

  /**
   * Gets county from API response
   * @param rawData API response data
   * @returns county if it exists or null
   */
  getMun(rawData: any[]): Mun | null {
    if (rawData != null) {
      let mun: Mun = {
        id: rawData[0].fid,
        code: rawData[0].code,
        name: rawData[0].name,
        NUTiii: rawData[0].nutiii
      }
      return mun;
    }
    return null;
  }

  /**
   * Gets fire layers for real event from API response
   * @param rawData API response data
   * @returns list of fire layers
   */
  getFireLayers(rawData: any[] | null): FirelocLayer[] {
    let layers: FirelocLayer[] = [];
    if (rawData !== null) {
      rawData.forEach(layer => {
        let newLayer: FirelocLayer = {
          id: layer.id,
          fireID: layer.fireid,
          designation: layer.design,
          serverLayer: layer.glyr,
          slug: layer.slug,
          store: layer.store,
          style: layer.style,
          workspace: layer.work
        };
        layers.push(newLayer);
      });
    }
    return layers;
  }

  // ----- DATE FILTERING

  /**
   * Method called upon date selection in Bootstrap Date Picker. 
   * Determines if selected date should be the start date, end date or update the date range.
   * 
   * If date range is complete, filters real events by the selected date range.
   * @param date date selected.
   */
  onDateSelection(date: NgbDate) {
    if (!this.fromDate && !this.toDate) {
      this.fromDate = date;
    } else if (this.fromDate && !this.toDate && date.after(this.fromDate)) {
      this.toDate = date;

      // format to 2 digit values
      let fromMonth = ("0" + this.fromDate.month).slice(-2);
      let fromDay = ("0" + this.fromDate.day).slice(-2);
      let toMonth = ("0" + this.toDate.month).slice(-2);
      let toDay = ("0" + this.toDate.day).slice(-2);

      let startDate = `${this.fromDate.year}-${fromMonth}-${fromDay}-00-00-00`;
      let endDate = `${this.toDate.year}-${toMonth}-${toDay}-23-59-59`;

      // send filter by date request
      this.eventServ.getRealEventsToken(startDate, endDate).subscribe(
        (result: any) => {
          // clear events
          this.events = [];

          // get filtered data
          this.getEventData(result.data);

          // update values for table and pagination
          this.events = JSON.parse(JSON.stringify(this.events));
          this.updateRowCount(this.events.length);
        }, error => { }
      );

    } else {
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

  // ----- LOCATION FILTERING

  /**
   * Receives map for location filtering. Sets up the onClick method for the map.
   * @param map leaflet map
   */
  receiveFilterMap(map: any) {
    this.filterMap = map;
    this.filterMap.on("click", (e: any) => { this.createPolyline(e.latlng); })
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
   * Filters real events by geographical location with API.
   */
  filterLoc() {
    // add final point to match first
    this.filterPoints.push(this.filterPoints[0]);

    // format points in WKT format
    let pointsWKTF = pointsToWKTF(this.filterPoints);

    // request filtered points
    this.eventServ.getRealEventsToken(undefined, undefined, pointsWKTF).subscribe(
      (result: any) => {
        // clear data
        this.events = [];

        // get data
        this.getEventData(result.data);

        // update values for table and pagination
        this.events = JSON.parse(JSON.stringify(this.events));
        this.updateRowCount(this.events.length);
      }, error => { }
    );
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
   * Opens or closes the display of a single real event's information details.
   * @param eventID event ID to display or -1 to close information
   */
  toggleEventView(eventID: number) {
    // reset map
    this.isMapVisible = false;
    // close event details
    if (eventID === -1) {
      this.isEventOpen = false;
      this.displayedHeaders = this.headers;
    }
    // open event details
    else {
      this.isEventOpen = true;
      this.displayedHeaders = this.openHeaders;

      // find event with selected event ID
      let eventIndex = this.events.findIndex(item => item.id === eventID);
      this.openEvent = this.events[eventIndex];
    }
  }

  /**
   * Opens or closes the display of the map for real event information.
   */
  toggleMapInfo() { this.isMapVisible = !this.isMapVisible; }

  /**
   * Receives map from child map component to display real event's location.
   * Method is incomplete due to API unavailability.
   * @param map leaflet map
   */
  receiveMap(map: any) {
    this.map = map;
    // Add event Location
    if (this.map !== null) { }
  }

  /**
   * Opens modals to create, update or delete a real event. Initializes the necessary data before opening a modal.
   * @param content modal content to display
   * @param modalType type of modal to open. Can be 'new', 'edit' or 'delete'
   */
  open(content: any, modalType: string) {
    // initialize according to modal
    switch (modalType) {
      case 'new':
        // initialize values
        this.newEventForm.reset();
        break;
      case 'edit':
        // initialize values
        this.editEventForm.reset();
        this.initEditData();
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
   * Initializes values to update real event
   */
  initEditData() {
    // prepare dates
    let start = new Date(this.openEvent.startTime);
    start.setMinutes(start.getMinutes() - start.getTimezoneOffset());

    let end = new Date(this.openEvent.endTime);
    end.setMinutes(end.getMinutes() - end.getTimezoneOffset());

    this.editEventForm.setValue({
      start: start.toISOString().slice(0, 16),
      end: end.toISOString().slice(0, 16),
      timezone: null,
      // optional
      name: this.openEvent.name,
      cause: this.openEvent.cause,
      type: this.openEvent.type,
      codSGIF: this.openEvent.codSGIF,
      codNCCO: this.openEvent.codNCCO,
    });
  }

  /**
   * Creates a new real event with the API if new event form is valid.
   */
  createNewEvent() {
    // check if form is valid
    if (this.newEventForm.valid) {
      // create request data
      let requestData: any = {
        start: this.newEventForm.get('start')?.value,
        end: this.newEventForm.get('end')?.value,
        geom: this.newEventForm.get('geom')?.value,
        epsg: this.newEventForm.get('epsg')?.value,
        timezone: this.newEventForm.get('timezone')?.value,
      }

      // add optional data if it exists
      let nameValue = this.newEventForm.get('name')?.value;
      let causeValue = this.newEventForm.get('cause')?.value;
      let typeValue = this.newEventForm.get('type')?.value;
      let codSGIFValue = this.newEventForm.get('codSGIF')?.value;
      let codNCCOValue = this.newEventForm.get('codNCCO')?.value;

      if (nameValue !== null) requestData.name = nameValue;
      if (causeValue !== null) requestData.causa = causeValue;
      if (typeValue !== null) requestData.tipo = typeValue;
      if (codSGIFValue !== null) requestData.codsgif = codSGIFValue;
      if (codNCCOValue !== null) requestData.codncco = codNCCOValue;

      // format dates
      requestData.start = datetimeToRequestString(requestData.start);
      requestData.end = datetimeToRequestString(requestData.end);

      this.eventServ.addRealEvent(requestData).subscribe(
        (result: any) => {
          // get data
          this.getEventData([result]);

          // update table and pagination
          this.events = JSON.parse(JSON.stringify(this.events));
          this.updateRowCount(this.events.length);
        }, error => { }
      );
    }

    // close
    this.modalService.dismissAll();
  }

  /**
   * Updates a real event if edit event form is valid.
   */
  updateEvent() {
    // check if form is valid
    if (this.editEventForm.valid) {

      // create request data
      let requestData: any = {
        start: this.editEventForm.get('start')?.value,
        end: this.editEventForm.get('end')?.value,
        timezone: this.editEventForm.get('timezone')?.value,
      }

      // add optional data if it exists
      let nameValue = this.editEventForm.get('name')?.value;
      let causeValue = this.editEventForm.get('cause')?.value;
      let typeValue = this.editEventForm.get('type')?.value;
      let codSGIFValue = this.editEventForm.get('codSGIF')?.value;
      let codNCCOValue = this.editEventForm.get('codNCCO')?.value;

      if (nameValue !== null) requestData.name = nameValue;
      if (causeValue !== null) requestData.causa = causeValue;
      if (typeValue !== null) requestData.tipo = typeValue;
      if (codSGIFValue !== null) requestData.codsgif = codSGIFValue;
      if (codNCCOValue !== null) requestData.codncco = codNCCOValue;

      // format dates
      requestData.start = datetimeToRequestString(requestData.start);
      requestData.end = datetimeToRequestString(requestData.end);

      // API request
      this.eventServ.updateRealEvent(this.openEvent.id, requestData).subscribe(
        (result: any) => {
          // get real event reference
          let eventIndex = this.events.findIndex(event => event.id === this.openEvent.id);
          let eventRef = this.events[eventIndex];

          // update data
          eventRef.name = result.name;
          eventRef.type = result.tipo;
          eventRef.startTime = result.start;
          eventRef.endTime = result.end;
          eventRef.cause = result.causa;
          eventRef.codSGIF = result.codsgif;
          eventRef.codNCCO = result.codncco;

          // update table
          this.events = JSON.parse(JSON.stringify(this.events));
        }, error => { }
      );
    }

    // close
    this.modalService.dismissAll();
  }

  /**
   * Checks if the user has confirmed the removal of a real event.
   * 
   * If there is confirmation, delete a real event with the API and update the displayed data.
   */
  removeEvent() {
    this.hasClickedRemove = true;
    // without checked confirmation, show error
    if (this.isConfChecked) {

      // remove dataset with API
      this.eventServ.deleteRealEvent(this.openEvent.id).subscribe(
        (result: any) => {
          // close user display
          this.isEventOpen = false;
          this.displayedHeaders = this.headers;

          // remove dataset from list
          let eventIndex = this.events.findIndex(item => item.id === this.openEvent.id);
          this.events.splice(eventIndex, 1);

          // update dataset table and pagination
          this.events = JSON.parse(JSON.stringify(this.events));
          this.updateRowCount(this.events.length);
        }, error => { }
      );

      // close
      this.modalService.dismissAll();
    }
  }

}
