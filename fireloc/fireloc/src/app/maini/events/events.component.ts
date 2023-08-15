import { Component, OnDestroy, OnInit } from '@angular/core';
import { Observable, Subscription } from 'rxjs';

// Style
import { faFireAlt, faTimes, faCalendar, faFileImage, faPlaceOfWorship, faCity, faChevronDown, faGlobeAfrica } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces & Constants
import { Event, EventAttribute, EventPlace, ServiceLayer } from 'src/app/interfaces/events';
import { MapSettings } from 'src/app/interfaces/maps';
import { Extent } from 'src/app/constants/mapext';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';
import { ContribService } from 'src/app/serv/rest/contrib.service';
import { EventService } from 'src/app/serv/rest/event.service';
import { MarkerService } from 'src/app/serv/leafmap/marker.service';

// Redux
import { EventActions } from 'src/app/redux/actions/eventActions';
import { select } from '@angular-redux/store';
import { selectDateRange, selectEvent } from 'src/app/redux/selectors';

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
  selector: 'app-events',
  templateUrl: './events.component.html',
  styleUrls: ['./events.component.css']
})
// DATES TO GEOSERVER ARE IN UTC
export class EventsComponent implements OnInit, OnDestroy {

  // icons
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
  isEventOpen: boolean = false;

  /**
   * list of events 
   */
  fullEvents: Event[] = [];
  /**
   * list of filtered events
   */
  filteredEvents: Event[] = [];

  // event information
  /**
   * open event index
   */
  eventIndex: number = -1;
  /**
   * open event ID
   */
  eventID: number = -1;
  /**
   * open event place name
   */
  eventPlaceName: string = '';
  /**
   * open event start date
   */
  startDate: (number | string)[] = [];
  /**
   * open event end date
   */
  endDate: (number | string)[] | null = null;
  /**
   * list of open event service layers
   */
  eventLayers: ServiceLayer[] = [];
  /**
   * list of open event attributes
   */
  eventAttr: EventAttribute[] = [];
  /**
   * list of open event contribution photos
   */
  eventPhotos: string[] = [];
  /**
   * open event contribution photo
   */
  contribPhoto: string = '';

  /**
   * active event information section toggle
   */
  eventInformationToggle = 1;

  // date range for information filtering
  /**
   * minimum date from date range for date filtering
   */
  minDate!: Date;
  /**
   * maximum date from date range for date filtering
   */
  maxDate!: Date;

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
   * Redux selector for events state
   */
  @select(selectEvent) reduxEvents$!: Observable<any>;
  /**
   * Redux selector for date range state
   */
  @select(selectDateRange) dateRange$!: Observable<any>;

  /**
   * holds redux subscription to update events information
   */
  eventsSub!: Subscription;
  /**
   * holds redux subscription to update date range information
   */
  dateRangeSub!: Subscription;

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
    private authServ: AuthService,
    private eventServ: EventService,
    private contribServ: ContribService,
    private markerServ: MarkerService,
    private eventActions: EventActions
  ) { this.isLoggedIn = this.authServ.isLoggedIn(); }

  /**
   * Subscribes to Redux for updates and gets events according to user logged status.
   */
  ngOnInit(): void {
    // improve performance with redux
    this.subscribeToRedux();

    // get fireloc events according to authentication
    this.isLoggedIn ? this.getAllEventsToken() : this.getAllEventsNoToken();
  }

  /**
   * Unsubscribe from Redux updates
   */
  ngOnDestroy(): void {
    // remove redux subscriptions
    if (this.eventsSub !== undefined) this.eventsSub.unsubscribe();
    if (this.dateRangeSub !== undefined) this.dateRangeSub.unsubscribe();
  }

  /**
   * Subscribe to redux updates.
   * Receive updates about events and date range.
   */
  subscribeToRedux() {
    // subscribe to get all fireloc events from redux
    this.eventsSub = this.reduxEvents$.subscribe(
      (event: any) => {
        this.fullEvents = event.events;
        if (this.fullEvents.length === 0) this.noEvents = true;
        this.loadingEvents = false;
      }
    );

    // subscribe to get date range from redux (constant updates)
    this.dateRangeSub = this.dateRange$.subscribe(
      (dateRange: any) => {
        // update range values
        this.minDate = dateRange.minDate;
        this.maxDate = dateRange.maxDate;

        // filter contributions
        this.filterEventsByDate(this.fullEvents);

        if (this.fullEvents.length !== 0) this.noEvents = false;
        this.loadingEvents = false;
      }
    );
  }

  /**
   * Gets events from the API if events list is empty. Does not require authentication.
   */
  getAllEventsNoToken() {
    // check if fireloc events are stored
    if (this.fullEvents.length === 0) {
      this.eventServ.getEventsNoToken().subscribe(
        (result: any) => {
          this.getEventInformation(result.data);
          this.loadingEvents = false;
        }, error => { }
      );
    }
  }

  /**
   * Gets events from the API if events list is empty. Requires authentication.
   */
  getAllEventsToken() {
    // check if fireloc events are stored
    if (this.fullEvents.length === 0) {
      this.eventServ.getEventsToken().subscribe(
        (result: any) => {
          this.getEventInformation(result.data);
          this.loadingEvents = false;
        }, error => { }
      );
    }
  }

  /**
   * Gets event information from API and converts it to the proper interfaces.
   * 
   * Sorts the list of events by date and saves the list in redux with an action dispatch.
   * See {@link EventActions} for more information about the dispatch.
   * @param APIEvents 
   */
  getEventInformation(APIEvents: any) {
    for (let event of APIEvents) {
      // date time values
      let startTime = getDateTimeValues(event.startime, false, 'pt');
      let endTime = null
      if (event.endtime !== null) {
        endTime = getDateTimeValues(event.endtime, false, 'pt');
      }
      let contribStart = getDateTimeValues(event.contribstart, false, 'pt');
      let contribEnd = getDateTimeValues(event.contribend, false, 'pt');

      // other atributes
      let id = event.id;
      let nearPlace = event.nearplace;

      // service layers
      let serviceLayers: ServiceLayer[] = [];
      for (let layer of event.floclyr) {
        let newLayer: ServiceLayer = {
          id: layer.id,
          gLayer: layer.glyr,
          slug: layer.slug,
          store: layer.store,
          style: layer.style,
          work: layer.work,
          design: layer.design
        }
        serviceLayers.push(newLayer);
      }

      // event contribution photos
      let contribPhotos: string[] = [];
      if (this.isLoggedIn) for (let contrib of event.flocctb) { contribPhotos.push(contrib.pic); }

      // event place
      let place = event.place;
      let placeObj: EventPlace = {
        id: place.fid,
        fregID: place.fregid,
        lugID: place.lugid,
        geom: place.geom,
        name: place.lugname,
      }

      // event attributes
      let attrObj: EventAttribute[] = [];
      for (let at of event.attr) {
        let newAt: EventAttribute = {
          id: at.id,
          slug: at.slug,
          name: at.name,
          value: at.value
        }
        attrObj.push(newAt);
      }

      // create Event object
      let eventObj: Event = {
        id: id,
        startTime: {
          year: startTime[0], month: startTime[1], day: startTime[2], hour: startTime[3], minute: startTime[4]
        },
        endTime: endTime !== null ? {
          year: endTime[0], month: endTime[1], day: endTime[2], hour: endTime[3], minute: endTime[4]
        } : null,
        contribStart: {
          year: contribStart[0], month: contribStart[1], day: contribStart[2], hour: contribStart[3], minute: contribStart[4]
        },
        contribEnd: {
          year: contribEnd[0], month: contribEnd[1], day: contribEnd[2], hour: contribEnd[3], minute: contribEnd[4],
        },
        nearPlace: nearPlace,
        contributionPhotos: contribPhotos,
        layers: serviceLayers,
        place: placeObj,
        attributes: attrObj,
      }

      // add event to list
      this.fullEvents.push(eventObj);
    }

    // sort fireloc events by start date
    this.fullEvents.sort((a, b) => {
      // form dates from values
      let firstDate = new Date(Number(a.startTime.year), Number(a.startTime.month) - 1, Number(a.startTime.day));
      let secondDate = new Date(Number(b.startTime.year), Number(b.startTime.month) - 1, Number(b.startTime.day));
      // sort 
      return firstDate.getTime() - secondDate.getTime();
    });

    // save fireloc events in redux
    this.eventActions.addEvents(this.fullEvents);
  }

  // ----- DATE FILTER
  /**
   * Filters events by date.
   * @param events list of events to filter
   */
  filterEventsByDate(events: Event[]) {
    this.filteredEvents = events.filter((event) => {
      // get date values from group date
      let eventYear = event.startTime.year;
      let eventMonth = event.startTime.month;
      let eventDay = event.startTime.day;

      if (typeof (eventYear) === 'number' && typeof (eventMonth) === 'number' && typeof (eventDay) === 'number') {
        let eventDate = new Date(eventYear, eventMonth - 1, eventDay);
        // add to filtered array if date is within date range
        return eventDate >= this.minDate && eventDate <= this.maxDate;
      }

      // default is add to the array
      return true;
    });
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
    this.filteredEvents = this.fullEvents;
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

  // open event information display
  /**
   * Opens event section to display the information of a single event.
   * @param event selected event to display
   * @param index index of selected event
   */
  openEvent(event: Event, index: number) {
    // set variables
    this.isEventOpen = true;
    this.eventIndex = index;
    this.eventPhotos = [];

    // remove all layers from redux
    this.eventActions.clearEventLayers();

    // if clicked on the same event, close it
    if (event.id === this.eventID) {
      this.closeEvent();
    } else {
      // get event information
      this.eventID = event.id;
      this.startDate = [event.startTime.day, event.startTime.month, event.startTime.year];
      this.endDate = event.endTime !== null ? [event.endTime.day, event.endTime.month, event.endTime.year] : null;
      this.eventLayers = event.layers;
      this.eventPlaceName = event.place.name;
      this.eventAttr = event.attributes;

      // start loading event contribution photos
      for (let photoString of event.contributionPhotos) { this.getContribPhoto(photoString.substring(1)); }
    }
  }

  /**
   * Closes open event information section
   */
  closeEvent() {
    // reset variables
    this.eventID = -1;
    this.eventIndex = -1;
    this.isEventOpen = false;
    this.eventPhotos = [];
    this.contribPhoto = '';

    // remove all layers from redux
    this.eventActions.clearEventLayers();
  }

  /**
   * Changes displayed event information
   * @param option event section to display
   */
  seeEventInformation(option: number) { this.eventInformationToggle = option; }

  /**
   * Gets contribution photo from API. See {@link ContribService} for more information.
   * @param photoName name of contribution photo
   */
  getContribPhoto(photoName: string) {
    this.contribServ.getContributionPhoto(photoName).subscribe(
      (result: any) => {
        let photoEncoded = result.data;
        let photoData = 'data:image/jpg;base64,' + photoEncoded;
        this.eventPhotos.push(photoData);
      }, error => { }
    );
  }

  // open contribution photo in popup window
  /**
   * Open Bootstrap modal with a contribution photo for better visualization of said photo.
   * @param content modal content to display
   * @param photo name of contribution photo
   */
  openContribPhoto(content: any, photo: string) {
    this.contribPhoto = photo;
    this.modalService.open(content, { centered: true, size: 'xl' });
  }

  /**
   * Adds or removes event service layers in redux to show in map.
   * 
   * INCOMPLETE METHOD DUE TO API UNAVAILABILITY.
   * @param ev selection event from checkbox input
   * @param layer event service layer
   */
  selectEventLayer(ev: any, layer: ServiceLayer) {
    // add layer
    if (ev.target.checked) this.eventActions.addEventLayer(layer);

    // remove layer
    else this.eventActions.removeEventLayer(layer);
  }

}