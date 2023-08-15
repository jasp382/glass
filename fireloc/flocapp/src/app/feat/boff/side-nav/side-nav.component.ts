import { Component, OnInit } from '@angular/core';
import { Router, Event, NavigationEnd } from '@angular/router';

// Fort Awesome
import {
  faUserAlt,
  faUserFriends,
  faCamera,
  faFire,
  faLayerGroup,
  faAlignJustify,
  faChartPie,
  faGlobeAfrica,
  faSatelliteDish,
  faTable,
  faVectorSquare,
  faUserCircle,
  faSignOutAlt,
  faAngleLeft
} from '@fortawesome/free-solid-svg-icons';

// Constants
import { SidebarConstants } from 'src/app/constants/boffNav';

// NGRX
import { AppState } from '../../../stores/app-state';
import { Store } from '@ngrx/store';

import * as userSelector from '../../../stores/users/users.reducer';

import { User } from 'src/app/interfaces/users';

/**
 * Side navigation component.
 * 
 * Displays a navigation bar used on the left side of the Backoffice interface.
 */
@Component({
  selector: 'feat-side-nav',
  templateUrl: './side-nav.component.html',
  styleUrls: ['./side-nav.component.css']
})
export class SideNavComponent implements OnInit {

  /**
   * flag to determine if geospatial menu is open or closed
   */
  isGeoMenuOpen = false;
  /**
   * current active navigation section
   */
  activeNavItem = 0;
  /**
   * flag to determine if navigation is open or collapsed
   */
  isNavCollapsed = false;

  // icons
  /**
   * users section icon
   */
  userIcon = faUserAlt;
  /**
   * groups section icon
   */
  groupIcon = faUserFriends;
  /**
   * contributions section icon
   */
  contribIcon = faCamera;
  /**
   * events section icon
   */
  eventIcon = faFire;
  /**
   * layers section icon
   */
  layerIcon = faLayerGroup;
  /**
   * legend section icon
   */
  legIcon = faAlignJustify;
  /**
   * graphs section icon
   */
  graphIcon = faChartPie;
  /**
   * geospatial menu icon
   */
  geoIcon = faGlobeAfrica;
  /**
   * satellite datasets section icon
   */
  satIcon = faSatelliteDish;
  /**
   * raster datasets section icon
   */
  rasterIcon = faTable;
  /**
   * vetorial datasets section icon
   */
  vectIcon = faVectorSquare;
  /**
   * profile icon
   */
  profileIcon = faUserCircle;
  /**
   * logout icon
   */
  outIcon = faSignOutAlt;
  /**
   * arrow icon
   */
  arrowIcon = faAngleLeft;

  /**
   * user name information
   */
  cuser: User|null = null;
  userName: string = ''

  /**
   * Subscribes to router events to check the active page URL.
   * @param router Angular router
   * @param authServ authentication service
   * @param userServ users service
   */
  constructor(
    private store: Store<AppState>,
    private router: Router,
    //private authServ: AuthService,
    //private userServ: UserService
  ) {
    this.router.events.subscribe((event: Event) => { if (event instanceof NavigationEnd) this.checkUrl(); });
  }

  ngOnInit(): void {
    // Update user when state is updated
    this.store
      .select(userSelector.getCurrentUser)
      .subscribe((cuser: User|null) => {
        this.cuser = cuser;
        if (this.cuser !== null) {
          this.userName = this.cuser.first_name + ' ' + this.cuser.last_name;
        }
      })
  }

  /**
   * Collapses or expands navigation bar
   */
  toggleSideNav() { this.isNavCollapsed = !this.isNavCollapsed; }

  /**
   * Opens or closes geospatial dropdown menu
   */
  openGeoMenu() { this.isGeoMenuOpen = !this.isGeoMenuOpen; }

  /**
   * Activates the correct navigation section with the current page URL.
   */
  checkUrl() {
    // get last part of url
    var urlSegment = this.router.url.split('/').pop();

    // check which nav item should be active
    switch (urlSegment) {
      case "users":
        this.activeNavItem = 1;
        break;
      case "groups":
        this.activeNavItem = 2;
        break;
      case "contribs":
        this.activeNavItem = 3;
        break;
      case "events":
        this.activeNavItem = 4;
        break;
      case "real-events":
        this.activeNavItem = 5;
        break;
      case "layers":
        this.activeNavItem = 6;
        break;
      case "legend":
        this.activeNavItem = 7;
        break;
      case "graphs":
        this.activeNavItem = 8;
        break;
      case "satellite":
        this.activeNavItem = 9;
        this.isGeoMenuOpen = true;
        break;
      case "raster":
        this.activeNavItem = 10;
        this.isGeoMenuOpen = true;
        break;
      case "vetorial":
        this.activeNavItem = 11;
        this.isGeoMenuOpen = true;
        break;
      default:
        this.activeNavItem = 0;
    }
  }

  /**
   * Selects the navigation section and navigates to the appropriate page.
   * Also emits the current active section for parent component.
   * @param itemID section ID
   */
  selectNavCategory(itemID: number) {
    this.activeNavItem = itemID;
    //this.activeNavItemEmitter.emit(itemID);
    switch (itemID) {
      case 1: this.router.navigate([SidebarConstants.usersLinks[0].url]); break;
      case 2: this.router.navigate([SidebarConstants.usersLinks[1].url]); break;
      case 3: this.router.navigate([SidebarConstants.contribLinks[0].url]); break;
      case 4: this.router.navigate([SidebarConstants.contribLinks[1].url]); break;
      case 5: this.router.navigate([SidebarConstants.otherLinks[0].url]); break;
      case 6: this.router.navigate([SidebarConstants.mapLinks[0].url]); break;
      case 7: this.router.navigate([SidebarConstants.mapLinks[1].url]); break;
      case 8: this.router.navigate([SidebarConstants.mapLinks[2].url]); break;
      case 9: this.router.navigate([SidebarConstants.geosLinks[0].url]); break;
      case 10: this.router.navigate([SidebarConstants.geosLinks[1].url]); break;
      case 11: this.router.navigate([SidebarConstants.geosLinks[2].url]); break;
      default: break;
    }
  }

  /**
   * Gets user name information from API with user service. See {@link UserService} for more details.
   */
  getUserName() {
    /*this.userServ.getUser().subscribe(
      (result: any) => {
        let firstName = result.first_name;
        let lastName = result.last_name;
        this.userName = `${firstName} ${lastName}`;
      }, error => { }
    );*/
  }

  /**
   * Logs out the user with authentication service. See {@link AuthService} for more details.
   */
  logout() { }

}
