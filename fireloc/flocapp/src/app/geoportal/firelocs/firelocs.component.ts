import { Component, OnInit } from '@angular/core';

// Style
import { faPlus, faFireAlt, faTimes, faCalendar, faFileImage, faPlaceOfWorship, faCity, faChevronDown, faGlobeAfrica } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces & Constants
import { Fireloc, FirelocAux } from 'src/app/interfaces/fireloc';
import { Token } from 'src/app/interfaces/login';
import { MapSettings } from 'src/app/interfaces/maps';
import { Extent } from 'src/app/constants/mapext';
import { ViewFirelocLayer } from 'src/app/interfaces/layers';

// Services
import { MarkerService } from 'src/app/serv/leafmap/marker.service';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as loginSelector from '../../stores/login/login.reducer';
import * as firelocSelector from '../../stores/flocs/flocs.reducer';
import * as firelocActions from '../../stores/flocs/flocs.actions';
import * as leafActions from '../../stores/leaf/leaf.actions';

// Util
import { getDateTimeValues } from 'src/app/util/helper';
import { pointsToWKTF } from 'src/app/util/formatter';



/**
 * Geoportal Events component.
 * 
 * Displays a list of events sorted by date. It is also possible to view a single event's information.
 * 
 * Users can also filter events by location and time period.
 */
@Component({
  selector: 'app-firelocs',
  templateUrl: './firelocs.component.html',
  styleUrls: ['./firelocs.component.css']
})
export class FirelocsComponent implements OnInit {

  token: Token|null = null;

  // icons
  plusIcon = faPlus;
  /**
   * drop icon for dropdowns
   */
  dropIcon = faChevronDown;
  /**
   * globe icon for location filtering
   */
  locIcon = faGlobeAfrica;
  /**
   * fire icon for fire
   */
  fireIcon = faFireAlt;
  /**
   * close icon for closing information
   */
  closeIcon = faTimes;
  /**
   * calendar icon for date information
   */
  calendarIcon = faCalendar;
  /**
   * photo icon for photo information
   */
  photoIcon = faFileImage;
  /**
   * icon for 'Município'
   */
  munIcon = faPlaceOfWorship;
  /**
   * icon for 'Freguesia'
   */
  fregIcon = faCity;

  /**
   * flag to determine user logged status
   */
  isLoggedIn: boolean = false;

  // event checks
  /**
   * flag to determine if events are being loaded from API or Redux
   */
  loadingEvents: boolean = true;
  /**
   * flag to determine if events list is empty
   */
  noEvents: boolean = false;
  /**
   * flag to determine if a single event's information is being displayed
   */
  isFlocOpen: boolean = false;

  /**
   * list of events 
   */
  fireloc: Fireloc[] = [];
  flocAux: FirelocAux[] = [];

  /**
   * list of filtered events
   */
  filteredFireloc: Fireloc[] = [];

  // event information
  /**
   * open event index
   */
  flocIdx: number = -1;

  /**
   * open event ID
   */
  flocID: number = -1;
  /**
   * open event place name
   */
  flocPlaceName: string = '';

  /**
   * open event start date
   */
  startDate: (number | string)[] = [];
  /**
   * open event end date
   */
  endDate: (number | string)[] = [];
  /**
   * list of open event service layers
   */
  //eventLayers: ServiceLayer[] = [];
  /**
   * list of open event attributes
   */
  //eventAttr: EventAttribute[] = [];
  /**
   * list of open event contribution photos
   */
  flocPhotos: string[] = [];
  /**
   * open event contribution photo
   */
  contribPhoto: string = '';

  /**
   * active event information section toggle
   */
  flocInfoToggle = 1;

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
    domElem: "filter-map-geoEvents",
    mapContainer: "filterMapGeoEvents",
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
   * Constructor for the Geoportal events component. Initializes user logged status.
   * @param modalService Bootstrap modal service
   * @param authServ authentication service. See {@link AuthService}.
   * @param eventServ event service. See {@link EventService}.
   * @param contribServ contribution service. See {@link ContribService}.
   * @param markerServ map marker service. See {@link MarkerService}.
   * @param eventActions Redux event actions. See {@link EventActions}.
   */
  constructor(
    private modalService: NgbModal,
    private store: Store<AppState>,
    private markerServ: MarkerService,
  ) { }

  /**
   * Subscribes to Redux for updates and gets events according to user logged status.
   */
  ngOnInit(): void {
    // Update Firelocs State
    this.store
      .select(loginSelector.getLoginToken)
      .subscribe((logState: Token|null) => {
        this.token = logState;

        this.store.dispatch(firelocActions.GetFireloc(
          {payload: {token: this.token, step: '7'}}
        ));
      })
    
    // Login State
    this.store
      .select(loginSelector.getLoginStatus)
      .subscribe((logStatus: boolean) => {
        this.isLoggedIn = logStatus;
    });

    // Get Firelocs current state
    this.store
      .select(firelocSelector.getFireloc)
      .subscribe((flocs: Fireloc[]) => {
        this.fireloc = flocs;

        this.loadingEvents = false;

        this.noEvents = !this.fireloc.length ? true: false;

        // Update Fireloc Aux object
        if (this.fireloc.length) {
          this.getFirelocInfo(this.fireloc);
        }
      })
  }

  getFirelocInfo(flocs: Fireloc[]) {
    for (let floc of flocs) {
      let ctbStart: (string|number)[] = getDateTimeValues(floc.ctbstart, false, 'pt');
      let ctbEnd: (string|number)[] = getDateTimeValues(floc.ctbend, false, 'pt');

      let startTime: (string|number)[]|null = null;
      let endTime: (string|number)[]|null = null;

      if (floc.startime !== null) {
        startTime = getDateTimeValues(floc.startime, false, 'pt');
      }

      if (floc.endtime !== null) {
        endTime = getDateTimeValues(floc.endtime, false, 'pt');
      }

      let faux: FirelocAux = {
        startTime: startTime !== null ? {
          year: startTime[0], month: startTime[1], day: startTime[2],
          hour: startTime[3], minute: startTime[4]
        } : null,
        endTime: endTime !== null ? {
          year: endTime[0], month: endTime[1], day: endTime[2],
          hour: endTime[3], minute: endTime[4]
        } : null,
        contribStart: {
          year: ctbStart[0], month: ctbStart[1],
          day: ctbStart[2], hour: ctbStart[3],
          minute: ctbStart[4]
        },
        contribEnd: {
          year: ctbEnd[0], month: ctbEnd[1],
          day: ctbEnd[2], hour: ctbEnd[3],
          minute: ctbEnd[4]
        }
      }

      this.flocAux.push(faux);
    }
  }

  // open fireloc information display
  /**
   * Opens event section to display the information of a single event.
   * @param event selected event to display
   * @param index index of selected event
   */
  openFireloc(floc: Fireloc, i: number) {
    // set variables
    this.isFlocOpen = true;
    this.flocIdx = i;
    this.flocPhotos = [];

    // if clicked on the same fireloc, close it
    if (floc.id === this.flocID) {
      this.closeFireloc();
    } else {
      this.flocID = floc.id;
      this.startDate = [
        this.flocAux[this.flocIdx].contribStart.day,
        this.flocAux[this.flocIdx].contribStart.month,
        this.flocAux[this.flocIdx].contribStart.year
      ];
      this.endDate = [
        this.flocAux[this.flocIdx].contribEnd.day,
        this.flocAux[this.flocIdx].contribEnd.month,
        this.flocAux[this.flocIdx].contribEnd.year
      ];
      this.flocPlaceName = floc.place === null ? floc.freg.name : floc.place.lugname;
    }
  }

  /**
   * Closes open event information section
   */
  closeFireloc() {
    // reset variables
    this.flocID = -1;
    this.flocIdx = -1;
    this.isFlocOpen = false;
    this.flocPhotos = [];
    this.contribPhoto = '';
  }

  /**
   * Changes displayed event information
   * @param option event section to display
   */
  seeFlocInfo(option: number) { this.flocInfoToggle = option; }

  addFlocToMap(layer: ViewFirelocLayer) {
    this.store.dispatch(leafActions.AddWMS({payload: layer}));
  }

  // ----- LOCATION FILTER

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
   * Clears the location filter information.
   */
  clearLocFilter() {
    // reset variables
    this.pointCounter = 0;
    this.filterPoints = [];

    // clear map
    this.markerServ.clearPolyGroup(this.filterPolygroup);

    // show unfiltered events
    this.filteredFireloc = this.fireloc;
  }

  // TODO UPDATE WHEN API IS AVAILABLE
  /**
   * Filters events by geographical location. 
   * 
   * INCOMPLETE METHOD DUE TO API UNAVAILABILITY.
   */
  filterLoc() {
    // add final point to match first
    this.filterPoints.push(this.filterPoints[0]);
    // format points in WKT format
    let pointsWKTF = pointsToWKTF(this.filterPoints);
  }

}
