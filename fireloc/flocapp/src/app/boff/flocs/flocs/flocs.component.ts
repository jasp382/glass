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
import { Token } from 'src/app/interfaces/login';
import { Fireloc, FirelocAux } from 'src/app/interfaces/fireloc';

// NGRX
import { AppState } from '../../../stores/app-state';
import { Store } from '@ngrx/store';

import * as loginSelector from '../../../stores/login/login.reducer';
import * as firelocSelector from '../../../stores/flocs/flocs.reducer';
import * as firelocActions from '../../../stores/flocs/flocs.actions';

// Services
import { MarkerService } from 'src/app/serv/leafmap/marker.service';


/**
 * Backoffice Events component.
 * 
 * Displays a list of FireLoc events. A single event can be viewed, edited or deleted.
 * It is also possible to filter the events with search terms, by location or by time period.
 */
@Component({
  selector: 'boff-flocs',
  templateUrl: './flocs.component.html',
  styleUrls: ['./flocs.component.css']
})
export class FlocsComponent implements OnInit {

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
  flocs: Fireloc[] = [];

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

  token: Token|null = null;

  constructor(
    private modalService: NgbModal,
    private markerServ: MarkerService,
    private store: Store<AppState>,
  ) { }

  ngOnInit(): void {
    // Update Firelocs States
    this.store
      .select(loginSelector.getLoginToken)
      .subscribe((logState: Token|null) => {
        this.token = logState;

        if (this.token !== null) {
          this.store.dispatch(firelocActions.GetAllFireloc({payload: this.token}));
        }
      });
    
    // Get Firelocs current state
    this.store
      .select(firelocSelector.getAllFireloc)
      .subscribe((flocs: Fireloc[]) => {
        this.flocs = flocs;
      })
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

}
