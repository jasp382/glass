import { Component, OnDestroy, OnInit } from '@angular/core';

// Fort Awesome
import {
  faFireAlt,
  faTimes,
  faCalendar,
  faTag,
  faBolt
} from '@fortawesome/free-solid-svg-icons';

// Interfaces
import { RealEvent, RealEventDate } from 'src/app/interfaces/realEvents';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';
import { RealEventService } from 'src/app/serv/rest/real-event.service';

// Redux
import { select } from '@angular-redux/store';
import { Observable, Subscription } from 'rxjs';
import { RealEventActions } from 'src/app/redux/actions/realEventActions';
import { selectLanguage, selectRealEvent } from 'src/app/redux/selectors';

// Util
import { getDateTimeValues } from 'src/app/util/helper';

/**
 * Geoportal Real Events component.
 * 
 * Displays a list of real events. It is also possible to view a single real event's information.
 * 
 */
@Component({
  selector: 'app-real-events',
  templateUrl: './real-events.component.html',
  styleUrls: ['./real-events.component.css']
})
export class RealEventsComponent implements OnInit, OnDestroy {

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
  fullEvents: RealEvent[] = [];

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

  /**
   * Redux selector for real events state
   */
  @select(selectRealEvent) reduxEvents$!: Observable<any>;
  /**
   * Redux selector for language state
   */
  @select(selectLanguage) langRedux$!: Observable<any>;
  /**
   * holds redux subscription to update list of real events
   */
  eventsSub!: Subscription;
  /**
   * holds redux subscription to update app language information
   */
  langSub!: Subscription;

  /**
   * Constructor for Geoportal real events component. Initializes the user's logged status.
   * @param authServ authentication service. See {@link AuthService}.
   * @param realEventServ real event service. See {@link RealEventService}.
   * @param realEventActions real event Redux actions. See {@link RealEventActions}.
   */
  constructor(
    private authServ: AuthService,
    private realEventServ: RealEventService,
    private realEventActions: RealEventActions,
  ) { this.isLoggedIn = this.authServ.isLoggedIn(); }

  /**
   * Subscribes to Redux for updates.
   * Gets real events according to logged status.
   */
  ngOnInit(): void {
    // improve performance with redux
    this.subscribeToRedux();

    // get fireloc events according to authentication
    this.isLoggedIn ? this.getRealEventsToken() : this.getRealEventsNoToken();
  }

  /**
   * Unsubscribe from Redux updates
   */
  ngOnDestroy(): void {
    // remove redux subscriptions
    if (this.eventsSub !== undefined) this.eventsSub.unsubscribe();
    if (this.langSub !== undefined) this.langSub.unsubscribe();
  }

  /**
   * Subscribes to Redux to get updates about real events and current app language.
   */
  subscribeToRedux() {
    // subscribe to get all fireloc events from redux
    this.eventsSub = this.reduxEvents$.subscribe(
      (realEvent: any) => {
        this.fullEvents = realEvent.events;
        if (this.fullEvents.length === 0) this.noEvents = true;
        else this.noEvents = false;
        this.loadingEvents = false;
      }
    );
    // subscribe to get app language changes
    this.langSub = this.langRedux$.subscribe((language: string) => { this.language = language; });
  }

  /**
   * Gets real events from API without an authentication token.
   */
  getRealEventsNoToken() {
    // check if fireloc events are stored
    if (this.fullEvents.length === 0) {
      this.realEventServ.getRealEventsNoToken().subscribe(
        (result: any) => {
          // if there are no real events in API, finish loading and inform user
          this.getEventInformation(result.data);
        }, error => { this.loadingEvents = false; }
      );
    }
  }

  /**
   * Gets real events from API with an authentication token.
   */
  getRealEventsToken() {
    // check if fireloc events are stored
    if (this.fullEvents.length === 0) {
      this.realEventServ.getRealEventsToken().subscribe(
        (result: any) => { this.getEventInformation(result.data); },
        error => { this.loadingEvents = false; }
      );
    }
  }

  /**
   * Gets real event information from the API. Support different app languages.
   * 
   * Dispatches an action to save the events in Redux for performance optimization. See {@link RealEventActions} for more information.
   * @param APIEvents list of events from the API request result
   */
  getEventInformation(APIEvents: any) {
    for (let event of APIEvents) {
      // date time values
      let start = getDateTimeValues(event.start, false, 'pt');
      let end = getDateTimeValues(event.end, false, 'pt');

      // start date values
      let startDate: RealEventDate = { year: start[0], month: start[1], day: start[2], minute: start[3], hour: start[4], }

      // end date values
      let endDate: RealEventDate = { year: end[0], month: end[1], day: end[2], minute: end[3], hour: end[4], }

      let eventName = '';
      if (this.language === 'pt') eventName = event.name ? event.name : "Sem Nome";
      else eventName = event.name ? event.name : "No Name"; // language is 'en'

      let eventPlace = '';
      if (this.language === 'pt') eventPlace = event.place ? event.place : "Sem Localização";
      else eventPlace = event.place ? event.place : 'No Location'; // language is 'en'

      // define real event object
      let eventObj: RealEvent = {
        startTime: startDate,
        endTime: endDate,
        cause: event.causa,
        name: eventName,
        place: eventPlace,
        type: event.tipo,
        codncco: event.codncco,
        codsgif: event.codsgif,
      }

      // add event to list of events
      this.fullEvents.push(eventObj);
    }

    // add events to redux
    this.realEventActions.addRealEvents(this.fullEvents);
  }

  /**
   * Opens the event information to display details about a single event.
   * @param event 
   * @param index 
   */
  openEvent(event: RealEvent, index: number) {
    // set variables
    this.isEventOpen = true;
    this.eventIndex = index;

    // remove all layers from redux
    //this.eventActions.clearEventLayers();

    // get event information
    this.startDate = [event.startTime.day, event.startTime.month, event.startTime.year];
    this.endDate = [event.endTime.day, event.endTime.month, event.endTime.year];
    this.eventPlace = event.place;
    this.eventName = event.name;
    this.eventCause = event.cause;
  }

  /**
   * Changes the opened event information displayed
   * @param option section number to be displayed
   */
  seeEventInformation(option: number) { this.eventInformationToggle = option; }

  /**
   * Closes the event information display
   */
  closeEvent() {
    // reset variables
    this.eventIndex = -1;
    this.isEventOpen = false;

    // remove all layers from redux
    //this.eventActions.clearEventLayers();
  }
}
