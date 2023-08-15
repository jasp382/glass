import { Component, OnInit } from '@angular/core';

// Fort Awesome
import {
  faFireAlt,
  faTimes,
  faCalendar,
  faTag,
  faBolt
} from '@fortawesome/free-solid-svg-icons';

// Interfaces
import { FireEvent } from 'src/app/interfaces/events';
import { Token } from 'src/app/interfaces/general';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as loginSelector from '../../stores/login/login.reducer';
import * as eventsActions from '../../stores/events/events.actions';
import * as eventSelector from '../../stores/events/events.reducer';

// Util
import { getDateTimeValues } from 'src/app/util/helper';

/**
 * Geoportal Real Events component.
 * 
 * Displays a list of real events. It is also possible to view a single real event's information.
 * 
 */
@Component({
  selector: 'app-events',
  templateUrl: './events.component.html',
  styleUrls: ['./events.component.css']
})
export class EventsComponent implements OnInit {

  /**
   * flag to determine the user's logged status
   */
  isLoggedIn: boolean = false;

  /**
   * current app language
   */
  language: string = 'pt';

  /**
   * flag to determine if events are being loaded
   */
  loadingEvents: boolean = true;
  /**
   * flag to determine if events list is empty
   */
  noEvents: boolean = false;

  // icons
  /**
   * fire icon for fire information
   */
  fireIcon = faFireAlt;
  /**
   * close icon to close information
   */
  closeIcon = faTimes;
  /**
   * calendar icon for dates
   */
  calendarIcon = faCalendar;
  /**
   * icon for event name
   */
  tagIcon = faTag;
  /**
   * icon for event cause
   */
  dangerIcon = faBolt;

  /**
   * flag to determine if a single event's information is being displayed
   */
  isEventOpen: boolean = false;

  /**
   * list of real events
   */
  fireEvents:FireEvent[] = [];

  // event information
  /**
   * open event index
   */
  eventIndex: number = -1;
  /**
   * open event place
   */
  eventPlace: string = '';
  /**
   * open event name
   */
  eventName: string = '';
  /**
   * open event cause
   */
  eventCause: string = '';
  /**
   * open event start date
   */
  startDate: (string | number)[] = [];
  /**
   * open event end date
   */
  endDate: (string | number)[] = [];

  /**
   * flag to determine the section of event information being displayed
   */
  eventInformationToggle = 1;

  token: Token|null = null;

  constructor(
    private store: Store<AppState>,
  ) { }

  /**
   * Subscribes to Redux for updates.
   * Gets real events according to logged status.
   */
  ngOnInit(): void {
    // Update Fire Events State
    this.store
      .select(loginSelector.getLoginToken)
      .subscribe((logState: Token|null) => {
        this.token = logState;

        this.store.dispatch(eventsActions.GetFireEvents(
          {payload: this.token}
        ));
      });
    
    // Login State
    this.store
      .select(loginSelector.getLoginStatus)
      .subscribe((logStatus: boolean) => {
        this.isLoggedIn = logStatus;
    });

    // Get Fire Events current state
    this.store
      .select(eventSelector.getFireEvents)
      .subscribe((events: FireEvent[]) => {
        this.fireEvents = events;

        this.loadingEvents = false;

        this.noEvents = !this.fireEvents.length ? true : false;
      });
  }

  /**
   * Opens the event information to display details about a single event.
   * @param event 
   * @param index 
   */

  openEvent(event: FireEvent, index: number) {}

}
