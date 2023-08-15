import { Component, OnInit } from '@angular/core';

// Fort Awesome
import {
  faUsers,
  faCamera,
  faFireAlt,
  faUserFriends
} from '@fortawesome/free-solid-svg-icons';

// Chart JS
import { ChartDataSets, ChartType } from 'chart.js';
import { Color, Label } from 'ng2-charts';

// Interfaces
import { MapSettings } from 'src/app/interfaces/maps';

// Constants
import { Extent } from 'src/app/constants/mapext';
import { firelocMarker } from 'src/app/constants/mapMarkers';

// Services
import { MarkerService } from 'src/app/serv/leafmap/marker.service';
import { UserService } from 'src/app/serv/rest/users/user.service';
import { GroupService } from 'src/app/serv/rest/users/group.service';
import { AuthService } from 'src/app/serv/rest/users/auth.service';

// Util
import { numberFormatter } from 'src/app/util/formatter';

/**
 * Backoffice Dashboard component.
 * Displays a quick general view of statistical information about the FireLoc system. 
 * 
 * Contains charts to display the number of contributions and identified events in the last 30 days.
 * Contains the number of users, contributions, identified fires and user groups in the system.
 * Features a map to represent the 5 most recent identified fires by the FireLoc system.
 * 
 * Component is incomplete due to API unavailability.
 */
@Component({
  selector: 'boff-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  // icons
  /**
   * icon for users
   */
  userIcon = faUsers;
  /**
   * icon for contributions
   */
  contribIcon = faCamera;
  /**
   * icon for identified fires
   */
  fireIcon = faFireAlt;
  /**
   * icon for user groups
   */
  groupIcon = faUserFriends;

  // header information
  /**
   * logged user's name
   */
  userName: string = '';
  /**
   * greeting according to local time
   */
  timeGreeting: string = 'Bom Dia';

  // common chart settings
  /**
   * list of chart legend items
   */
  chartLegend = false;
  /**
   * list of chart plugins
   */
  chartPlugins = [];
  /**
   * defines the chart types
   */
  chartType: ChartType = 'line';

  /**
   * contributions chart datasets. Fake data due to API unavailability
   */
  contribsChartData: ChartDataSets[] = [{
    data: [40, 45, 42, 50, 48, 75, 38, 40, 45, 42, 50, 48, 75, 38, 40, 45,
      42, 50, 48, 75, 38, 40, 45, 42, 50, 48, 75, 38, 60, 50],
    fill: false
  }];
  /**
   * contributions chart labels
   */
  contribsChartLabels: Label[] = Array(30).fill('Contribuições');
  /**
   * contributions chart settings
   */
  contribsChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    elements: {
      point: {
        radius: 1,
        backgroundColor: '#F5A32A',
        borderColor: '#F5A32A',
        hitRadius: 4,
      }
    },
    plugins: {
      tooltip: {
        mode: 'point'
      }
    },
    scales: {
      yAxes: [{
        gridLines: {
          display: false,
          ticks: {
            display: false
          }
        },
        display: false,
      }],
      xAxes: [{
        gridLines: {
          display: false,
          ticks: {
            display: false
          }
        },
        display: false,
      }],
    }
  };
  /**
   * contributions chart colors
   */
  contribsChartColors: Color[] = [{ borderColor: '#F5A32A' }];

  /**
   * events chart datasets. Fake data due to API unavailability
   */
  fireChartData: ChartDataSets[] = [{
    data: [40, 45, 42, 50, 48, 75, 38, 40, 45, 42, 50, 48, 75, 38, 40, 45,
      42, 50, 48, 75, 38, 40, 45, 42, 50, 48, 75, 38, 60, 50],
    fill: false
  }];
  /**
   * events chart labels
   */
  fireChartLabels: Label[] = Array(30).fill('Eventos');
  /**
   * events chart settings
   */
  fireChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    elements: {
      point: {
        radius: 1,
        backgroundColor: '#B00600',
        borderColor: '#B00600',
        hitRadius: 4,
      }
    },
    plugins: {
      tooltip: {
        mode: 'point'
      }
    },
    scales: {
      yAxes: [{
        gridLines: {
          display: false,
          ticks: {
            display: false
          }
        },
        display: false,
      }],
      xAxes: [{
        gridLines: {
          display: false,
          ticks: {
            display: false
          }
        },
        display: false,
      }],
    }
  };
  /**
   * events chart colors
   */
  fireChartColors: Color[] = [{ borderColor: '#B00600' }];

  // statistics
  /**
   * total number of users
   */
  totalUsers: string = '';
  /**
   * total number of contributions
   */
  totalContribs: string = '';
  /**
   * total number of identified fires
   */
  totalFires: string = '';
  /**
   * total number of user groups
   */
  totalGroups: string = '';

  /**
   * dashboard map settings
   */
  mapsettings: MapSettings = {
    domElem: "boff-map",
    mapContainer: "boffMap",
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
   * reference to dashboard map
   */
  map: any = null;

  /**
   * Empty constructor for the Backoffice dashboard component.
   * @param markerServ map marker service. See {@link MarkerService}.
   * @param authServ authentication service. See {@link AuthService}.
   * @param userServ user service. See {@link UserService}.
   * @param groupServ group service. See {@link GroupService}.
   */
  constructor(
    private markerServ: MarkerService,
    private authServ: AuthService,
    private userServ: UserService,
    private groupServ: GroupService
  ) { }

  /**
   * Initializes data for header information and statistics
   */
  ngOnInit(): void {
    // get header information
    this.getTimeGreeting();
    this.getUserName();

    // get statistics
    this.getUsers();
    this.getGroups();
  }

  /**
   * Defines greeting according to local time
   */
  getTimeGreeting() {
    let date = new Date();
    let time = date.getHours();

    // set greeting according to local time
    if (time < 12 && time >= 6) this.timeGreeting = 'Bom Dia';
    else if (time < 19 && time >= 12) this.timeGreeting = 'Boa Tarde';
    else this.timeGreeting = 'Boa Noite';
  }

  /**
   * Get user name for greeting from API
   */
  getUserName() {
    this.userServ.getUser().subscribe((result: any) => { this.userName = result.first_name; }, error => { });
  }

  /**
   * Gets user statistics from API
   */
  getUsers() {
    this.userServ.getUsers().subscribe(
      (result: any) => {
        // get user count
        let userCount = result.data.length;
        this.totalUsers = numberFormatter(userCount);
      }, error => { }
    );
  }

  /**
   * Gets user group statistics from API
   */
  getGroups() {
    this.groupServ.getGroups(false, false).subscribe(
      (result: any) => {
        // get group count
        let groupCount = result.data.length;
        this.totalGroups = numberFormatter(groupCount);
      }, error => { }
    );
  }

  // get contributions
  // ...

  // get fires
  // ...

  /**
   * Receives map from child component. Adds custom fire markers for the five most recent identified fires.
   * @param $event leaflet map
   */
  receiveMap($event: any) {
    this.map = $event;
    this.addFireMakers();
  }

  /**
   * Adds recent fire markers to map. Method is incomplete due to API unavailability
   */
  addFireMakers() {
    // TODO CHANGE WITH API INFO
    if (this.map !== null) {
      this.markerServ.addCustomMarkerToMap(this.map, 40.185587, -8.415428, firelocMarker);
      this.markerServ.addCustomMarkerToMap(this.map, 38.680655, -9.101792, firelocMarker);
      this.markerServ.addCustomMarkerToMap(this.map, 37.538282, -7.914592, firelocMarker);
      this.markerServ.addCustomMarkerToMap(this.map, 41.160316, -8.530177, firelocMarker);
      this.markerServ.addCustomMarkerToMap(this.map, 41.256602, -6.947244, firelocMarker);
    }
  }

  /**
   * Logs out the user
   */
  logout() { this.authServ.logout(); }
}
