import { Component, OnInit } from '@angular/core';

// Style
import {
  faChevronDown,
  faGlobeAfrica,
  faUserAlt,
  faCalendarDay,
  faSearch,
  faCamera,
  faMapMarkerAlt,
  faTrash,
  faTimes
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
 * Backoffice Contributions component.
 * 
 * Displays a list of FireLoc contributions. A single contribution can be viewed or deleted.
 * It is also possible to filter the contributions with search terms, by location, by user or by time period.
 */
@Component({
  selector: 'boff-contribs',
  templateUrl: './contributions.component.html',
  styleUrls: ['./contributions.component.css']
})
export class ContributionsComponent implements OnInit {

  // icons
  /**
   * icon for dropdown menus
   */
  dropIcon = faChevronDown;
  /**
   * icon for location filter
   */
  locIcon = faGlobeAfrica;
  /**
   * icon for user filter
   */
  userIcon = faUserAlt;
  /**
   * icon for dates
   */
  dateIcon = faCalendarDay;
  /**
   * icon for searches
   */
  searchIcon = faSearch;
  /**
   * icon to display contribution photo
   */
  cameraIcon = faCamera;
  /**
   * icon to display contribution map
   */
  mapIcon = faMapMarkerAlt;
  /**
   * icon for contribution deletion
   */
  deleteIcon = faTrash;
  /**
   * icon to close information
   */
  closeIcon = faTimes;

  // TODO REPLACE WITH API DATA
  /**
   * list of FireLoc contributions. Currently holds fake data due to API unavailability
   */
  contribs: any[] = [
    { id: 1, place: 'Lisboa', date: '12/08/2019 12:17:20', fire: 'Sem Informação', dir: 180, sunDir: 80 },
    { id: 2, place: 'Coimbra', date: '20/09/2019 13:08:19', fire: 'Lousã - Coimbra', dir: 270, sunDir: 72 },
    { id: 3, place: 'Porto', date: '21/09/2022 20:17:59', fire: 'Sem Informação', dir: 160, sunDir: 70 },
    { id: 4, place: 'Soure', date: '28/09/2020 03:08:54', fire: 'Sem Informação', dir: 120, sunDir: 50 },
    { id: 5, place: 'Coimbra', date: '10/05/2020 08:45:08', fire: 'Sem Informação', dir: 60, sunDir: 25 },
  ];
  /**
   * list of users for contribution user filter. Currently holds fake data due to API unavailability
   */
  users: any[] = [
    { id: 1, name: 'João Patriarca', email: 'admin@fireloc.com', selected: false },
    { id: 2, name: 'Raquel Ferreira', email: 'fireloc@fireloc.com', selected: false },
    { id: 3, name: 'João Carvalho', email: 'riskmanager@gmail.com', selected: false },
    { id: 4, name: 'Sandra Almeida', email: 'volunteer@gmail.com', selected: false },
  ];

  /**
   * list of table headers for table component
   */
  headers: TableHeader[] = [
    { objProperty: 'id', columnLabel: '#' },
    { objProperty: 'place', columnLabel: 'Localização' },
    { objProperty: 'date', columnLabel: 'Data' },
    { objProperty: 'fire', columnLabel: 'Fogo Associado' },
    { objProperty: 'dir', columnLabel: 'Direção' },
    { objProperty: 'sunDir', columnLabel: 'Direção do Sol' }
  ];
  /**
   * list of headers to be displayed when a single contribution is closed
   */
  displayedHeaders = this.headers;

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

  // user filter
  /**
   * search terms to search for users in users filter
   */
  userSearchTerms: string = '';
  /**
   * list of filtered users
   */
  filteredUsers: any[] = this.users;
  /**
   * user email to filter contributions
   */
  filterUserEmail: string = '';

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

  // contribution details
  /**
   * flag to determine if a single contribution's information is being displayed 
   */
  isContribOpen: boolean = false;
  /**
   * list of headers to be displayed when a single contribution is open
   */
  openHeaders: TableHeader[] = this.headers.filter((_, index) => index < 3);
  /**
   * reference to open contribution
   */
  openContrib: any = {};
  /**
   * flag to determine if contribution map is visible
   */
  isMapVisible: boolean = false;

  // contribution map
  /**
   * contribution map settings
   */
  mapsettings: MapSettings = {
    domElem: "contrib-map",
    mapContainer: "contribMap",
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
   * reference for contribution map
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
  rowCount: number = this.contribs.length;

  // remove contribution
  /**
  * flag to determine if user has confirmed contribution removal
  */
  isConfChecked: boolean = false;
  /**
   * flag to determine if user has decided to remove a contribution
   */
  hasClickedRemove: boolean = false;

  /**
   * Empty constructor for the Backoffice events component.
   * @param markerServ map marker service. See {@link MarkerService}.
   * @param modalService Bootstrap modal service
   */
  constructor(private markerServ: MarkerService, private modalService: NgbModal) { }

  /**
   * Empty method.
   */
  ngOnInit(): void { }

  /**
   * Updates search terms.
   * Searches events by location and fire name in table component. 
   * See {@link TableComponent#filterDataSearchContributions} for more information.
   * @param searchTerms new search terms
   */
  searchContribs(searchTerms: string) {
    // ignore clear search event
    if (typeof (searchTerms) === 'string') this.searchTerms = searchTerms;
  }

  /**
   * Searches users by name in users filter
   * @param searchTerms user search terms
   */
  searchUsers(searchTerms: string) {
    this.userSearchTerms = searchTerms;

    // if search is clear, show all users
    if (this.userSearchTerms.length === 0) this.filteredUsers = JSON.parse(JSON.stringify(this.users));
    else
      this.filteredUsers = this.users.filter(user =>
        user.name.toLowerCase().includes(this.userSearchTerms.toLowerCase())
      );
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
   * Filters contributions by geographical location. 
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
   * Selects a user to add to user filter. Filters contributions by selected users.
   * @param userID selected user ID
   */
  selectUser(userID: number) {
    // deselect other users
    this.users = this.users.map(user => { return { ...user, selected: false }; });
    this.filteredUsers = this.filteredUsers.map(user => { return { ...user, selected: false }; });

    // select user
    let userIndex = this.users.findIndex(user => user.id === userID);
    let filteredUserIndex = this.filteredUsers.findIndex(user => user.id === userID);

    this.users[userIndex].selected = true;
    this.filteredUsers[filteredUserIndex].selected = true;

    // update user filter
    this.filterUserEmail = this.users[userIndex].email;
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
   * Opens or closes the display of a single contribution's information details.
   * @param contribID contribution ID to display or -1 to close information
   */
  toggleContribView(contribID: number) {
    // close contribution details
    if (contribID === -1) {
      this.isContribOpen = false;
      this.displayedHeaders = this.headers;
    }
    // open contribution details
    else {
      this.isContribOpen = true;
      this.displayedHeaders = this.openHeaders;

      // find contribution with selected contribution ID
      let contribIndex = this.contribs.findIndex(item => item.id === contribID);
      this.openContrib = this.contribs[contribIndex];
    }
  }

  /**
   * Opens or closes the display of the map for contribution information.
   */
  toggleMapImage() { this.isMapVisible = !this.isMapVisible; }

  /**
   * Receives map from child map component to display event's location.
   * Method is incomplete due to API unavailability.
   * @param map leaflet map
   */
  receiveMap(map: any) {
    this.map = map;
    // Add contribution Location
    if (this.map !== null) {
      // TODO CHANGE WITH CONTRIBUTION COORDINATES
      this.markerServ.addMarkerToMap(this.map, 40.185587, -8.415428);
    }
  }

  /**
   * Opens a Bootstrap modal to display content.
   * @param content modal content to display
   */
  open(content: any) {
    // reset
    this.isConfChecked = false;
    this.hasClickedRemove = false;

    this.modalService.open(content, { centered: true, size: 'lg' });
  }

  // TODO COMPLETE WITH API
  /**
   * Checks if the user has confirmed the removal of a contribution.
   * 
   * If there is confirmation, delete a contribution with the API and update the displayed data.
   * 
   * Method is incomplete due to API unavailability.
   */
  deleteContrib() {
    this.hasClickedRemove = true;
    // without checked confirmation, show error
    if (this.isConfChecked) {
      // remove contrib from list
      let contribIndex = this.contribs.findIndex(item => item.id === this.openContrib.id);
      this.contribs.splice(contribIndex, 1);

      // update table and pagination
      this.contribs = JSON.parse(JSON.stringify(this.contribs));
      this.updateRowCount(this.contribs.length);

      // ...

      // close and reset
      this.isContribOpen = false;
      this.displayedHeaders = this.headers;
      this.isConfChecked = false;
      this.hasClickedRemove = false;
      this.modalService.dismissAll();
    }
  }

}
