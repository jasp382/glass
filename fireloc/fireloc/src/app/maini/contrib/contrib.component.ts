import { Component, EventEmitter, OnDestroy, OnInit, Output } from '@angular/core';
import { SafeUrl } from '@angular/platform-browser';

// Style
import { faClock, faLocationArrow, faCompass, faSun, faTimes, faChevronDown, faGlobeAfrica, faFireAlt, faSearch } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Components
import { LoginComponent } from 'src/app/auth/login/login.component';
import { SignupComponent } from 'src/app/auth/signup/signup.component';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';
import { ContribService } from 'src/app/serv/rest/contrib.service';
import { MarkerService } from 'src/app/serv/leafmap/marker.service';

// Interfaces & Constants
import { Contribution, Geom, ContribDate, ContributionDateGroup } from 'src/app/interfaces/contribs';
import { MapSettings } from 'src/app/interfaces/maps';
import { enMonths, ptMonths } from 'src/app/constants/dateMonths';
import { Extent } from 'src/app/constants/mapext';

// Redux
import { select } from '@angular-redux/store';
import { Observable, Subscription } from 'rxjs';
import { selectAllContribs, selectUserContribs, selectDateRange, selectUser, selectLanguage } from 'src/app/redux/selectors';
import { ContributionActions } from 'src/app/redux/actions/contributionActions';

// Util
import { avgLatLong, checkUserHasPermissions, getDateTimeValues, getLatLongValues } from 'src/app/util/helper';
import { pointsToWKTF } from 'src/app/util/formatter';

/**
 * Default contribution photo when none is available
 */
const defaultContribPhoto = 'data:image/jpg;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAQAAADa613fAAAAaElEQVR42u3PQREAAAwCoNm/9CL496ABuREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREWkezG8AZQ6nfncAAAAASUVORK5CYII=';

/**
 * Geoportal Contributions component.
 * 
 * Displays a list of contributions sorted and grouped by date. It is also possible to view a single contribution's information.
 * Contributions are only shown to authenticated users.
 * 
 * If a user has permissions, they are capable of viewing all FireLoc contributions as well as their own. 
 * Otherwise they can only view their own contributions.
 * 
 * Users with permissions can also filter all contributions by location, event and time period.
 * 
 */
@Component({
  selector: 'app-contrib',
  templateUrl: './contrib.component.html',
  styleUrls: ['./contrib.component.css']
})
export class ContribComponent implements OnInit, OnDestroy {

  /**
   * emitter for which contribution list is selected
   */
  @Output('allContribsSelected') toggleEmitter = new EventEmitter<boolean>();

  // icons
  /**
   * drop icon for dropdowns
   */
  dropIcon = faChevronDown;
  /**
   * clock icon for time values
   */
  clockIcon = faClock;
  /**
   * globe icon for location filtering
   */
  filterLocIcon = faGlobeAfrica;
  /**
   * fire icon for fire
   */
  fireIcon = faFireAlt;
  /**
   * search icon for search
   */
  searchIcon = faSearch;
  /**
   * location icon for coordinates
   */
  locIcon = faLocationArrow;
  /**
   * direction icon for direction
   */
  directionIcon = faCompass;
  /**
   * sun icon for sun direction
   */
  sunIcon = faSun;
  /**
   * close icon for closing information
   */
  closeIcon = faTimes;

  // user checks
  /**
   * flag to determine user logged status
   */
  isLoggedIn: boolean = false;
  /**
   * flag to determine user permission status
   */
  hasPermission: boolean = false;

  /**
   * current app language value
   */
  language: string = 'pt';

  // contribution checks
  /**
   * flag to determine if contributions are being loaded from API or Redux
   */
  loadingContribs: boolean = true;
  /**
   * flag to determine the contributions list is empty
   */
  noContribs: boolean = false;
  /**
   * flag to determine if all contributions list is being shown
   */
  allContribSelected: boolean = true;
  /**
   * flag to determine if a single contribution's information is being displayed
   */
  isContribOpen: boolean = false;

  // contributions list information
  /**
   * list of contributions grouped and sorted by date
   */
  fullContributionsDateGroups: ContributionDateGroup[] = [];
  /**
   * list of filtered contributions grouped and sorted by date
   */
  filteredContributionsDateGroups: ContributionDateGroup[] = [];

  // all contributions data
  /**
   * list of all FireLoc contributions
   */
  allContributions: Contribution[] = [];
  /**
   * list of all FireLoc contributions grouped and sorted by date
   */
  allContributionsDateGroups: ContributionDateGroup[] = [];

  // user contributions data
  /**
   * list of user contributions
   */
  userContributions: Contribution[] = [];
  /**
   * list of user contributions grouped and sorted by date
   */
  userContributionsDateGroups: ContributionDateGroup[] = [];

  // contribution information
  /**
   * open contribution ID
   */
  contribId: number = -1;
  /**
   * open contribution index
   */
  contribIndex: number = -1;
  /**
   * open contribution photo
   */
  contribPhoto: SafeUrl = defaultContribPhoto;
  /**
   * open contribution location
   */
  contribLocation: string = '';
  /**
   * open contribution time
   */
  contribTime: string = '';
  /**
   * open contribution latitude coordinate
   */
  contribLat: number | string = 0;
  /**
   * open contribution longitude coordinate
   */
  contribLong: number | string = 0;
  /**
   * open contribution direction
   */
  contribDirection: number = 0;
  /**
   * open contribution sun direction
   */
  contribSun: number | null = -1;        // optional

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
    domElem: "filter-map-geoContrib",
    mapContainer: "filterMapGeoContrib",
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

  // TODO UPDATE EVENT DATA WHEN API IS AVAILABLE
  // event filter
  /**
   * list of FireLoc events
   */
  events: any[] = [];
  /**
   * search terms for event search
   */
  eventSearchTerms: string = '';
  /**
   * list of events filtered by search terms
   */
  filteredEvents: any[] = this.events;
  /**
   * selected event name
   */
  filterEventName: string = '';

  // redux
  /**
   * Redux selector for all contributions state
   */
  @select(selectAllContribs) allContributions$!: Observable<any>;
  /**
   * Redux selector for user contributions state
   */
  @select(selectUserContribs) userContributions$!: Observable<any>;
  /**
   * Redux selector for date range state
   */
  @select(selectDateRange) dateRange$!: Observable<any>;
  /**
   * Redux selector for user state
   */
  @select(selectUser) userRedux$!: Observable<any>;
  /**
   * Redux selector for language state
   */
  @select(selectLanguage) langRedux$!: Observable<any>;

  // redux subscriptions references
  /**
   * holds redux subscription to update all contributions list information
   */
  allContribSub!: Subscription;
  /**
   * holds redux subscription to update user contributions list information
   */
  userContribSub!: Subscription;
  /**
   * holds redux subscription to update date range information
   */
  dateRangeSub!: Subscription;
  /**
   * holds redux subscription to update user information
   */
  userSub!: Subscription;
  /**
   * holds redux subscription to update app language information
   */
  langSub!: Subscription;

  /**
   * Constructor for the Geoportal contributions component. Initializes user logged status.
   * @param modalService Bootstrap modal service
   * @param authServ authentication service. See {@link AuthService}.
   * @param contribServ contribution service. See {@link ContribService}.
   * @param markerServ map marker service. See {@link MarkerService}.
   * @param contributionActions Redux contribution actions. See {@link ContributionActions}.
   */
  constructor(
    private modalService: NgbModal,
    private authServ: AuthService,
    private contribServ: ContribService,
    private markerServ: MarkerService,
    private contributionActions: ContributionActions
  ) { this.isLoggedIn = this.authServ.isLoggedIn(); }

  /**
   * Checks user permissions and get contributions according to logged status and permissions.
   * Subscribes to Redux for updates.
   */
  ngOnInit(): void {
    // check user permissions
    this.hasPermission = checkUserHasPermissions(this.isLoggedIn);

    // improve performance with redux
    this.subscribeToRedux();

    // check permissions and get contribution data
    if (this.hasPermission) {
      this.getAllContribs();
      this.getUserContribs();
    }
    else if (this.isLoggedIn && !this.hasPermission) {
      this.allContribSelected = false;
      this.getUserContribs();
    }

    if (this.isLoggedIn) {
      this.toggleEmitter.emit(this.allContribSelected);
      this.getEventsToken();
    }
    else this.getEventsNoToken();
  }

  /**
   * Unsubscribe from Redux updates
   */
  ngOnDestroy(): void {
    // remove redux subscriptions
    if (this.allContribSub !== undefined) this.allContribSub.unsubscribe();
    if (this.userContribSub !== undefined) this.userContribSub.unsubscribe();
    if (this.dateRangeSub !== undefined) this.dateRangeSub.unsubscribe();
    if (this.userSub !== undefined) this.userSub.unsubscribe();
    if (this.langSub !== undefined) this.langSub.unsubscribe();
  }

  /**
   * Subscribe to redux updates.
   * Receive updates about contributions, date range and app language.
   */
  subscribeToRedux() {
    // subscribe to get all contributions from redux (1 time action)
    this.allContribSub = this.allContributions$.subscribe(
      (contribs: any) => {
        this.allContributionsDateGroups = contribs;

        if (contribs.length === 0) this.noContribs = true;

        // display information
        if (this.allContribSelected && this.hasPermission) {
          this.fullContributionsDateGroups = contribs;
          // check if contributions are ready to be displayed
          if (contribs.length !== 0) this.loadingContribs = false;
        }
      }
    );

    // subscribe to get user contributions from redux (1 time action)
    this.userContribSub = this.userContributions$.subscribe(
      (contribs: any) => {
        this.userContributionsDateGroups = contribs;

        if (contribs.length === 0) this.noContribs = true;

        // display information
        if (!this.allContribSelected || !this.hasPermission) {
          this.fullContributionsDateGroups = contribs;
          // check if contributions are ready to be displayed
          if (contribs.length !== 0) this.loadingContribs = false;
        }
      }
    );

    // subscribe to get date range from redux (constant updates)
    this.dateRangeSub = this.dateRange$.subscribe(
      (dateRange: any) => {
        // update range values
        this.minDate = dateRange.minDate;
        this.maxDate = dateRange.maxDate;

        // filter contributions
        this.filterContributionsByDate(this.fullContributionsDateGroups);

        // check if contributions are ready to be displayed
        if (this.fullContributionsDateGroups.length !== 0) {
          this.noContribs = false;
          this.loadingContribs = false;
        }
      }
    );

    // subscribe to update UI if user has logged in
    this.userSub = this.userRedux$.subscribe(
      (user: any) => {
        this.isLoggedIn = this.authServ.isLoggedIn();
        // check user permissions
        this.hasPermission = checkUserHasPermissions(this.isLoggedIn);

        // check permissions and get contribution data
        if (this.hasPermission) {
          this.getAllContribs();
          this.getUserContribs();
        }
        else if (this.isLoggedIn && !this.hasPermission) {
          this.allContribSelected = false;
          this.getUserContribs();
        }

        if (this.isLoggedIn) {
          this.toggleEmitter.emit(this.allContribSelected);
          this.getEventsToken();
        }
      }
    );

    // subscribe to get app language changes
    this.langSub = this.langRedux$.subscribe((language: string) => { this.language = language; });
  }

  /**
   * Gets all FireLoc contributions from the API if contribution list is empty.
   * After getting contributions from API, store them in Redux for optimized performance.
   */
  getAllContribs() {
    // check if contributions are stored
    if (this.allContributionsDateGroups.length === 0) {
      // get all contributions from API
      this.contribServ.getContributions().subscribe(
        (result: any) => {
          for (let contrib of result.data) {
            // get initial contribution values
            let id = contrib.fid;
            let pic = contrib.pic;
            let location = '';
            if (this.language === 'pt') location = contrib.fire_name ? contrib.fire_name : 'Sem Localização';
            else location = contrib.fire_name ? contrib.fire_name : 'No Location'; // language is 'en'
            let [year, month, day, hour, minute] = getDateTimeValues(contrib.datehour, true, this.language);
            let date: ContribDate = {
              year: year,
              month: month,
              day: day
            };
            let dir = contrib.direction;
            let dsun = contrib.dsun;

            // create contribution object
            var contribution: Contribution = {
              fid: id,
              pic: pic,
              location: location,
              date: date,
              hour: hour,
              minute: minute,
              dir: dir,
              dsun: dsun,
              geom: []
            };

            // get geom info
            for (let geom of contrib.geom) {
              let pid = geom.pid;
              let [long, lat] = getLatLongValues(geom.geom);

              // create point object
              let point: Geom = {
                pid: pid,
                lat: lat,
                long: long
              };

              // add point to contribution object
              contribution.geom.push(point);
            }
            // add contribution to list of all contributions
            this.allContributions.push(contribution);
          }
          // group contributions by date
          this.groupContribByDate(this.allContributions, 'all');
        }, error => { }
      );
    }
  }

  /**
   * Gets user contributions from the API if contribution list is empty.
   * After getting contributions from API, store them in Redux for optimized performance.
   */
  getUserContribs() {
    // check if contributions are stored
    if (this.userContributionsDateGroups.length === 0) {
      // get user contributions from API
      let userID = localStorage.getItem('userId');
      this.contribServ.getContributions(userID).subscribe(
        (result: any) => {
          for (let contrib of result.data) {
            // get initial contribution values
            let id = contrib.fid;
            let pic = contrib.pic;
            let location = '';
            if (this.language === 'pt') location = contrib.fire_name ? contrib.fire_name : 'Sem Localização';
            else location = contrib.fire_name ? contrib.fire_name : 'No Location'; // language is 'en'
            let [year, month, day, hour, minute] = getDateTimeValues(contrib.datehour, true, this.language);
            let date: ContribDate = {
              year: year,
              month: month,
              day: day
            };
            let dir = contrib.direction;
            let dsun = contrib.dsun;

            // create contribution object
            var contribution: Contribution = {
              fid: id,
              pic: pic,
              location: location,
              date: date,
              hour: hour,
              minute: minute,
              dir: dir,
              dsun: dsun,
              geom: []
            };

            // get geom info
            for (let geom of contrib.geom) {
              let pid = geom.pid;
              let [long, lat] = getLatLongValues(geom.geom);

              // create point object
              let point: Geom = {
                pid: pid,
                lat: lat,
                long: long
              };

              // add point to contribution object
              contribution.geom.push(point);
            }
            // add contribution to list of all contributions
            this.userContributions.push(contribution);
          }
          // group contributions by date
          this.groupContribByDate(this.userContributions, 'user');
        },
        error => { }
      );
    }
  }

  // ----- DATE FILTER
  /**
   * Filters contributions by date. Supports multiple app languages.
   * @param contributions list of contributions to filter
   */
  filterContributionsByDate(contributions: ContributionDateGroup[]) {
    this.filteredContributionsDateGroups = contributions.filter((group) => {
      // get date values from group date
      let groupYear = group.date.year;
      let groupMonth;
      if (this.language === 'pt') {
        groupMonth = ptMonths.find(month => month.month === group.date.month)?.value;
        if (groupMonth === undefined)
          groupMonth = enMonths.find(month => month.month === group.date.month)?.value;
      }
      else {
        // language === 'en'
        groupMonth = enMonths.find(month => month.month === group.date.month)?.value;
        if (groupMonth === undefined)
          groupMonth = ptMonths.find(month => month.month === group.date.month)?.value;
      }
      let groupDay = group.date.day;

      if (typeof (groupYear) === 'number' && groupMonth != undefined && typeof (groupDay) === 'number') {
        let groupDate = new Date(groupYear, groupMonth, groupDay);
        // add to filtered array if date is within date range
        return (groupDate >= this.minDate && groupDate <= this.maxDate);
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

    // show unfiltered contributions
    this.fullContributionsDateGroups = this.allContributionsDateGroups;
    this.filterContributionsByDate(this.fullContributionsDateGroups);
  }

  // TODO UPDATE WHEN API IS AVAILABLE
  /**
   * Filters contributions by geographical location. 
   * 
   * INCOMPLETE METHOD DUE TO API UNAVAILABILITY.
   */
  filterLoc() {
    // add final point to match first
    this.filterPoints.push(this.filterPoints[0]);
    // format points in WKT format
    let pointsWKTF = pointsToWKTF(this.filterPoints);
  }

  // ----- EVENT FILTER

  // TODO UPDATE WHEN API IS AVAILABLE
  /**
   * Gets list of FireLoc events with user authentication. 
   * 
   * INCOMPLETE METHOD DUE TO API UNAVAILABILITY.
   */
  getEventsToken() {
    this.events = this.filteredEvents = [
      { id: 1, name: 'Sameiro' },
      { id: 2, name: 'Coimbra' },
      { id: 3, name: 'Lisboa' },
      { id: 4, name: 'Porto' },
    ];
  }
  // TODO UPDATE WHEN API IS AVAILABLE
  /**
   * Gets list of FireLoc events without user authentication. 
   * 
   * INCOMPLETE METHOD DUE TO API UNAVAILABILITY.
   */
  getEventsNoToken() {
    this.events = this.filteredEvents = [
      { id: 1, name: 'Sameiro' },
      { id: 2, name: 'Coimbra' },
      { id: 3, name: 'Lisboa' },
      { id: 4, name: 'Porto' },
    ];
  }

  /**
   * Searches events by name in events search filter
   * @param searchTerms search terms in the search input
   */
  searchEvents(searchTerms: string) {
    this.eventSearchTerms = searchTerms;

    // if search is clear, show all users
    if (this.eventSearchTerms.length === 0)
      this.filteredEvents = [...this.events];
    else
      this.filteredEvents = this.events.filter((event: any) =>
        event.name.toLowerCase().includes(this.eventSearchTerms.toLowerCase())
      );
  }

  // TODO UPDATE WHEN API IS AVAILABLE
  /**
   * Select event for contributions filtering by FireLoc event.
   * 
   * INCOMPLETE METHOD DUE TO API UNAVAILABILITY.
   * @param eventID selected FireLoc event ID
   */
  selectEvent(eventID: number) {
    // deselect other events
    this.events = this.events.map(event => { return { ...event, selected: false }; });
    this.filteredEvents = this.filteredEvents.map(event => { return { ...event, selected: false }; });

    // select event
    let eventIndex = this.events.findIndex(event => event.id === eventID);
    let filteredEventIndex = this.filteredEvents.findIndex(event => event.id === eventID);

    this.events[eventIndex].selected = true;
    this.filteredEvents[filteredEventIndex].selected = true;

    // update event filter
    this.filterEventName = this.events[eventIndex].name;
  }

  // -----

  /**
   * Gets contribution photo from API. See {@link ContribService} for more information.
   * @param photoName name of contribution photo
   */
  getContribPhoto(photoName: string) {
    this.contribServ.getContributionPhoto(photoName).subscribe(
      (result: any) => {
        let photoEncoded = result.data;
        this.contribPhoto = 'data:image/jpg;base64,' + photoEncoded;
      }, error => { }
    );
  }

  /**
   * Open Bootstrap modal with a contribution photo for better visualization of said photo.
   * @param content modal content to display
   */
  openContribPhoto(content: any) { this.modalService.open(content, { centered: true, size: 'xl' }); }

  /**
   * Displays all FireLoc contributions.
   */
  allContrib() {
    // change toggles
    this.toggleContribButtons();

    // show all contributions
    this.fullContributionsDateGroups = this.allContributionsDateGroups;
    this.filterContributionsByDate(this.fullContributionsDateGroups);
    if (this.allContributionsDateGroups.length === 0) this.noContribs = true;
    else this.noContribs = false;
  }

  /**
   * Displays user contributions.
   */
  myContrib() {
    // change toggles
    this.toggleContribButtons();

    // show user contributions 
    this.fullContributionsDateGroups = this.userContributionsDateGroups;
    this.filterContributionsByDate(this.fullContributionsDateGroups);
    if (this.userContributionsDateGroups.length === 0) this.noContribs = true;
    else this.noContribs = false;
  }

  /**
   * Opens contribution section to display the information of a single contribution.
   * @param contrib selected contribution to display
   * @param index index of selected contribution
   */
  openContribution(contrib: Contribution, index: number) {
    this.isContribOpen = true;
    this.contribIndex = index;

    // reset variables
    this.contribSun = -1;
    this.contribPhoto = defaultContribPhoto;

    // if clicked on the same contribution, close it
    if (contrib.fid === this.contribId) this.closeContribution();
    else {
      // get contribution photo
      this.getContribPhoto(contrib.pic);

      // get contribution information
      this.contribId = contrib.fid;
      this.contribLocation = contrib.location;
      this.contribTime = contrib.hour + ':' + contrib.minute;
      this.contribDirection = contrib.dir;
      [this.contribLat, this.contribLong] = avgLatLong(contrib.geom);
      if (contrib.dsun !== null) this.contribSun = contrib.dsun;
    }
  }

  /**
   * Closes open contribution information section
   */
  closeContribution() {
    // reset variables
    this.contribId = -1;
    this.contribIndex = -1;
    this.isContribOpen = false;
  }

  // ------------ helper methods ------------

  /**
   * Switches active contribution button - all or user
   */
  toggleContribButtons() {
    this.allContribSelected = !this.allContribSelected;
    this.toggleEmitter.emit(this.allContribSelected);
  }

  /**
   * Opens login modal. See {@link LoginComponent} for more details about the modal content.
   */
  openLogin() { this.modalService.open(LoginComponent, { centered: true }); }

  /**
   * Opens signup modal. See {@link SignupComponent} for more details about the modal content.
   */
  openRegister() { this.modalService.open(SignupComponent, { centered: true }); }

  /**
   * Checks if contribution date is already present in a list of contribution date groups
   * @param date date to check
   * @param contributionGroups list to check date against
   * @returns true if date is present, false if otherwise
   */
  checkDateAdded(date: ContribDate, contributionGroups: ContributionDateGroup[]) {
    return contributionGroups.some(function (el) {
      return (el.date.year === date.year && el.date.month === date.month && el.date.day === date.day)
    })
  }

  /**
   * Group contributions by contribution date.
   * @param contributions list of contributions to group
   * @param type type of contributions. Can be 'all' or 'user'
   */
  groupContribByDate(contributions: Contribution[], type: string) {
    let data = new Set(contributions.map(item => item.date));
    data.forEach((date) => {
      // check if date has already been added to array
      if (type === 'all') {
        let found = this.checkDateAdded(date, this.allContributionsDateGroups);

        // if date is not in group, add it
        if (!found) {
          // add to all contribution groups
          this.allContributionsDateGroups.push({
            date: date,
            // add contributions with this date
            contributions: contributions.filter(con => con.date.year === date.year
              && con.date.month === date.month
              && con.date.day === date.day)
          });
        }

      } else if (type === 'user') {
        let found = this.checkDateAdded(date, this.userContributionsDateGroups);

        // if date is not in group, add it
        if (!found) {
          // add to user contribution groups
          this.userContributionsDateGroups.push({
            date: date,
            // add contributions with this date
            contributions: contributions.filter(con => con.date.year === date.year
              && con.date.month === date.month
              && con.date.day === date.day)
          });
        }
      }
    });

    // sort and save contribution groups in redux
    this.sortContribByDate(type);
    this.loadingContribs = false;
  }

  /**
   * Sort contribution groups by date. 
   * 
   * Dispatches Redux action to save contribution. See {@link ContributionActions} for more information.
   * @param type type of contributions. Can be 'all' or 'user'
   */
  sortContribByDate(type: string) {
    if (type === 'all') {
      // sort date groups by date
      this.allContributionsDateGroups.sort((a, b) => {
        // get month values back
        let firstMonth;
        let secondMonth;

        // portuguese as language used
        if (this.language === 'pt') {
          firstMonth = ptMonths.find(month => month.month === a.date.month)?.value;
          secondMonth = ptMonths.find(month => month.month === b.date.month)?.value;
          // if month was not found in one language, try the other one
          if (firstMonth === undefined)
            firstMonth = enMonths.find(month => month.month === a.date.month)?.value;
          if (secondMonth === undefined)
            secondMonth = enMonths.find(month => month.month === a.date.month)?.value;
        }

        // english as language used
        else {
          firstMonth = enMonths.find(month => month.month === a.date.month)?.value;
          secondMonth = enMonths.find(month => month.month === b.date.month)?.value;
          // if month was not found in one language, try the other one
          if (firstMonth === undefined)
            firstMonth = ptMonths.find(month => month.month === a.date.month)?.value;
          if (secondMonth === undefined)
            secondMonth = ptMonths.find(month => month.month === a.date.month)?.value;
        }

        // sort dates, if months were found
        if (firstMonth !== undefined && secondMonth !== undefined) {
          // form dates from values
          let firstDate = new Date(Number(a.date.year), firstMonth, Number(a.date.day));
          let secondDate = new Date(Number(b.date.year), secondMonth, Number(b.date.day));
          return firstDate.getTime() - secondDate.getTime();
        }
        // default return same order
        return 1;
      });
      // save groups in redux
      this.contributionActions.saveAllContributions(this.allContributionsDateGroups);
    }
    else if (type === 'user') {
      // sort date groups by date
      this.userContributionsDateGroups.sort((a, b) => {
        // get month values back
        let firstMonth;
        let secondMonth;

        // portuguese as language used
        if (this.language === 'pt') {
          firstMonth = ptMonths.find(month => month.month === a.date.month)?.value;
          secondMonth = ptMonths.find(month => month.month === b.date.month)?.value;
          // if month was not found in one language, try the other one
          if (firstMonth === undefined)
            firstMonth = enMonths.find(month => month.month === a.date.month)?.value;
          if (secondMonth === undefined)
            secondMonth = enMonths.find(month => month.month === a.date.month)?.value;
        }

        // english as language used
        else {
          firstMonth = enMonths.find(month => month.month === a.date.month)?.value;
          secondMonth = enMonths.find(month => month.month === b.date.month)?.value;
          // if month was not found in one language, try the other one
          if (firstMonth === undefined)
            firstMonth = ptMonths.find(month => month.month === a.date.month)?.value;
          if (secondMonth === undefined)
            secondMonth = ptMonths.find(month => month.month === a.date.month)?.value;
        }

        // sort dates
        if (firstMonth !== undefined && secondMonth !== undefined) {
          // form dates from values
          let firstDate = new Date(Number(a.date.year), firstMonth, Number(a.date.day));
          let secondDate = new Date(Number(b.date.year), secondMonth, Number(b.date.day));
          return firstDate.getTime() - secondDate.getTime();
        }
        // default return same order
        return 1;
      });

      // save groups in redux
      this.contributionActions.saveUserContributions(this.userContributionsDateGroups);
    }
  }

}
