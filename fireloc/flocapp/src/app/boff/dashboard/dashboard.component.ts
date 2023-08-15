import { Component, OnInit } from '@angular/core';

// Fort Awesome
import {
  faUsers,
  faCamera,
  faFireAlt,
  faUserFriends
} from '@fortawesome/free-solid-svg-icons';

// Chart JS
//import { ChartDataSets, ChartType } from 'chart.js';
//import { Color, Label } from 'ng2-charts';

// Interfaces
import { MapSettings } from 'src/app/interfaces/maps';
import { Extent } from 'src/app/constants/mapext';
import { firelocMarker } from 'src/app/constants/mapMarkers';
import { User } from 'src/app/interfaces/users';
import { Token } from 'src/app/interfaces/general';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as userSelector from '../../stores/users/users.reducer';
import * as loginSelector from '../../stores/login/login.reducer';
import * as loginActions from '../../stores/login/login.actions';


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

  cuser: User = {
    id: 0,
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    token: [],
    usgroup: {
      id: 0, name: '', users: null, layers: null
    },
    attr: [],
    active: false
  };

  token: Token|null = null;
  userID: string = '';

  constructor(private store: Store<AppState>) { }

  ngOnInit(): void {
    // Get user current state
    // update state if necessary
    this.store
      .select(loginSelector.getLogUser)
      .subscribe((cuser: User|null) => {
        if (cuser !== null) {
          this.cuser = cuser;

          if (this.cuser !== null) {
            this.userName = this.cuser.first_name + ' ' +
              this.cuser.last_name;
          }
        } else {
          // We need to update current User state
          if (this.token === null && this.userID === '') {
            this.store
              .select(loginSelector.getTokenUserID)
              .subscribe((payload: any) => {
                this.token = payload.token;
                this.userID = payload.userid !== null ? payload.userid : '';

                if (this.token !== null && this.userID !== '') {
                  this.store.dispatch(loginActions.LoggedUser(
                    { payload: {token: this.token, userid: this.userID} }
                  ))
                }
              })
          } else if (this.token !== null && this.userID !== '') {
            this.store.dispatch(loginActions.LoggedUser(
              { payload: {token: this.token, userid: this.userID} }
            ));
          }
        }
      })
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
   * Logs out the user
   */
  logout() {  }
}
