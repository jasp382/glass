import { Component, OnInit } from '@angular/core';
import { Router, Event, NavigationEnd } from '@angular/router';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import { LoginState } from '../../stores/login/login.reducer';
import * as loginSelector from '../../stores/login/login.reducer';
import * as userActions from '../../stores/users/users.actions';


import { Token } from 'src/app/interfaces/general';

/**
 * Backoffice Main component.
 * Controls the information displayed in the Backoffice according to the selected section in the navigation bar.
 */
@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.css']
})
export class MainComponent implements OnInit {

  /**
   * current active navigation section
   */
  activePage: number = 0;

  token: Token|null = null;
  userid: string = '';

  /**
   * Constructor for the Backoffice main component. Checks the current URL after the navigation ends.
   * @param router Angular router
   */
  constructor(
    private router: Router,
    private store: Store<AppState>,
  ) {
    this.router.events.subscribe((event: Event) => {
      if (event instanceof NavigationEnd) {
        this.checkUrl(router.url);
      }
    })
  }

  ngOnInit(): void {
    // Get User Profile
    this.store
      .select(loginSelector.getFullState)
      .subscribe((logState: LoginState) => {
        this.token = logState.token;
        this.userid = logState.userid !== null ? logState.userid : '';

        console.log(logState);

        if (this.token !== null) {
          console.log(this.userid);
          this.store.dispatch(userActions.GetUser({payload: {
            token: this.token, userid: this.userid
          }}))
        }
      })
  }

  /**
   * Activates the correct navigation section according to current URL
   * @param url current URL provided by the router
   */
  checkUrl(url: string) {
    // get last part of url
    var urlSegment = url.split('/').pop();

    // check which page should be shown
    switch (urlSegment) {
      case "users":
        this.activePage = 1;
        break;
      case "groups":
        this.activePage = 2;
        break;
      case "contribs":
        this.activePage = 3;
        break;
      case "events":
        this.activePage = 4;
        break;
      case "real-events":
        this.activePage = 5;
        break;
      case "layers":
        this.activePage = 6;
        break;
      case "legend":
        this.activePage = 7;
        break;
      case "graphs":
        this.activePage = 8;
        break;
      case "satellite":
        this.activePage = 9;
        break;
      case "raster":
        this.activePage = 10;
        break;
      case "vetorial":
        this.activePage = 11;
        break;
      default:
        this.activePage = 0;
    }
  }

}
