import { Component, OnDestroy, OnInit } from '@angular/core';

// Angular Slider
import { ChangeContext, LabelType, Options } from '@angular-slider/ngx-slider';

// Interfaces
import { ContributionDateGroup } from 'src/app/interfaces/contribs';
import { Event } from 'src/app/interfaces/events';

// Constants
import { ptMonths } from 'src/app/constants/dateMonths';
import { enMonths } from 'src/app/constants/dateMonths';

// Redux
import { select } from '@angular-redux/store';
import { Observable, Subscription } from 'rxjs';
import { DateRangeActions } from 'src/app/redux/actions/dateRangeActions';
import { selectContribution, selectEvent, selectLanguage } from 'src/app/redux/selectors';

/**
 * Map footer component.
 * 
 * Contains a slider to select the date range to filter content in the Geoportal.
 */
@Component({
  selector: 'app-map-footer',
  templateUrl: './map-footer.component.html',
  styleUrls: ['./map-footer.component.css']
})
export class MapFooterComponent implements OnInit, OnDestroy {

  /**
   * current app language
   */
  language: string = 'pt';

  // contributions
  /**
   * list of all contributions grouped by date
   */
  allContributionsDateGroups: ContributionDateGroup[] = [];
  /**
   * list of user contributions grouped by date
   */
  userContributionsDateGroups: ContributionDateGroup[] = [];

  /**
   * list of FireLoc events
   */
  firelocEvents: Event[] = [];

  /**
   * selected date range
   */
  dateRange: Date[] = [];

  /**
   * minimum date in date range
   */
  minDate!: Date;
  /**
   * maximum date in date range
   */
  maxDate!: Date;

  /**
   * initial range minimum value
   */
  minValue: number = -1;
  /**
   * initial range maximum value
   */
  maxValue: number = -1;

  /**
   * slider options
   */
  options!: Options;

  /**
   * slider size for scrolling
   */
  sliderWidth!: number;
  /**
   * distance between ticks in the slider
   */
  sliderTickWidth: number = 40;

  // drag to scroll the slider
  /**
   * flag to detect if user has the mouse down
   */
  mouseDown = false;
  /**
   * drag slider start point
   */
  startX: any;
  /**
   * holds the amount of scrolling to move the slider
   */
  scrollLeft: any;

  /**
   * selector to subscribe to contribution lists information updates
   */
  @select(selectContribution) contributions$!: Observable<any>;
  /**
   * selector to subscribe to event list information updates
   */
  @select(selectEvent) events$!: Observable<any>;
  /**
   * selector to subscribe to current app language updates
   */
  @select(selectLanguage) langRedux$!: Observable<any>;

  /**
   * holds redux subscription to update contribution lists information
   */
  contribSub!: Subscription;
  /**
   * holds redux subscription to update event list information
   */
  eventsSub!: Subscription;
  /**
   * holds redux subscription to update current app language
   */
  languageSub!: Subscription;

  /**
   * Empty constructor.
   * @param dateRangeActions Redux date range actions. See {@link DateRangeActions}
   */
  constructor(private dateRangeActions: DateRangeActions) { }

  /**
   * Initializes Redux subscriptions, date range and slider options.
   */
  ngOnInit(): void {
    // improve performance with redux
    this.subscribeToRedux();

    // set slider date range
    this.dateRange = this.createDateRange();

    // set slider options
    this.updateSliderRange();

    // start showing slider at most recent date (scroll to the right)
    let container = document.getElementById("container");
    if (container !== null && container !== undefined) {
      setTimeout((container: any) => { container.scrollLeft = container.scrollWidth; }, 500, container);
    }
  }

  /**
   * Removes redux subscriptions and create date range.
   */
  ngOnDestroy(): void {
    // unsubscribe from redux events
    if (this.contribSub !== undefined) this.contribSub.unsubscribe();
    if (this.eventsSub !== undefined) this.eventsSub.unsubscribe();
    if (this.languageSub !== undefined) this.languageSub.unsubscribe();

    // remove date ranges
    this.dateRangeActions.removeValues();
  }

  /**
   * Subscribe to Redux to get updates on contributions, FireLoc events and language used.
   */
  subscribeToRedux() {
    // get updates about contribution state
    this.contribSub = this.contributions$.subscribe(
      (result: any) => {
        let allContribs = result.allContributions;
        let userContribs = result.userContributions;

        if (allContribs.length !== 0) {
          this.allContributionsDateGroups = allContribs;
          // update date range
          this.updateDateRange();

        } else if (userContribs.length !== 0) {
          this.userContributionsDateGroups = userContribs;
          // update date range
          this.updateDateRange();
        }
      }
    );

    // get updates about events
    this.eventsSub = this.events$.subscribe(
      (event: any) => {
        if (event.events.length !== 0 && this.firelocEvents.length === 0) {
          this.firelocEvents = event.events;
          // update date range
          this.updateDateRange();
        }
      }
    );

    // get app language
    this.languageSub = this.langRedux$.subscribe(
      (language: string) => {
        this.language = language;
        // update date range
        this.updateDateRange();
      }
    );
  }

  /**
   * Updates the date range. Dispatches a Redux action to allow other components to update their values as needed.
   */
  updateDateRange() {
    // update date range
    this.dateRange = this.createDateRange();
    this.updateSliderRange();

    this.minDate = new Date(this.minValue);
    this.maxDate = new Date(this.maxValue);

    // dispatch redux to update range values
    this.dateRangeActions.updateValues(this.minDate, this.maxDate);
  }

  /**
   * Creates date range with available information. Removes duplicate dates to get an accurate range.
   * 
   * Possible date ranges to be created are:
   * 
   * -> Default Range (1 month before current day)
   * 
   * -> FireLoc Events 
   * 
   * -> All Contributions
   * 
   * -> User Contributions
   * 
   * FireLoc Events and All Contributions
   * 
   * FireLoc Events and User Contributions
   * @returns date range created
   */
  createDateRange(): Date[] {
    const dates: Date[] = [];

    // if no data, create a default month range from today's date
    if (this.allContributionsDateGroups.length === 0
      && this.userContributionsDateGroups.length === 0
      && this.firelocEvents.length === 0) {

      // get todays date
      let today = new Date();

      // get date range for a month before today
      for (let i: number = 31; i >= 1; i--) {
        dates.push(new Date(today.getFullYear(), today.getMonth(), today.getDate() - i));
      }
      dates.push(today);
    }

    // if only fireloc events are available, create date range from them
    else if (this.firelocEvents.length !== 0
      && this.allContributionsDateGroups.length === 0
      && this.userContributionsDateGroups.length === 0) {

      this.firelocEvents.forEach((event) => {
        if (typeof (event.startTime.year) === 'number'
          && typeof (event.startTime.month) === 'number'
          && typeof (event.startTime.day) === 'number') {

          // add dates from fireloc events to date range
          dates.push(new Date(event.startTime.year, event.startTime.month - 1, event.startTime.day));
        }
      });
    }

    // if only contributions are available, create date range from them
    else if (this.allContributionsDateGroups.length !== 0
      && this.firelocEvents.length === 0) {

      this.allContributionsDateGroups.forEach((group) => {
        // check variable types
        if (typeof (group.date.year) === 'number'
          && typeof (group.date.month) === 'string'
          && typeof (group.date.day) === 'number') {

          // add dates from group to date range
          dates.push(new Date(group.date.year, this.translateMonthString(group.date.month), group.date.day));
        }
      });
    }

    // if only user contributions are available, create date range from them
    else if (this.allContributionsDateGroups.length === 0
      && this.userContributionsDateGroups.length !== 0
      && this.firelocEvents.length === 0) {

      this.userContributionsDateGroups.forEach((group) => {
        // check variable types
        if (typeof (group.date.year) === 'number'
          && typeof (group.date.month) === 'string'
          && typeof (group.date.day) === 'number') {

          // add dates from group to date range
          dates.push(new Date(group.date.year, this.translateMonthString(group.date.month), group.date.day));
        }
      });
    }

    // if fireloc events and all contributions are available, create date range from both
    else if (this.firelocEvents.length !== 0
      && this.allContributionsDateGroups.length !== 0) {

      // add dates from fireloc events
      this.firelocEvents.forEach((event) => {
        // check variable types
        if (typeof (event.startTime.year) === 'number'
          && typeof (event.startTime.month) === 'number'
          && typeof (event.startTime.day) === 'number') {

          // add dates from fireloc events to date range
          dates.push(new Date(event.startTime.year, event.startTime.month - 1, event.startTime.day));
        }
      });

      // add dates from all contributions
      this.allContributionsDateGroups.forEach((group) => {
        // check variable types
        if (typeof (group.date.year) === 'number'
          && typeof (group.date.month) === 'string'
          && typeof (group.date.day) === 'number') {

          // add dates from group to date range
          dates.push(new Date(group.date.year, this.translateMonthString(group.date.month), group.date.day));
        }
      });
    }

    // if fireloc events and only user contributions are available, create date range from both
    else if (this.firelocEvents.length !== 0
      && this.allContributionsDateGroups.length === 0
      && this.userContributionsDateGroups.length !== 0) {

      // add dates from fireloc events
      this.firelocEvents.forEach((event) => {
        // check variable types
        if (typeof (event.startTime.year) === 'number'
          && typeof (event.startTime.month) === 'number'
          && typeof (event.startTime.day) === 'number') {

          // add dates from fireloc events to date range
          dates.push(new Date(event.startTime.year, event.startTime.month - 1, event.startTime.day));
        }
      });

      // add dates from all contributions
      this.userContributionsDateGroups.forEach((group) => {
        // check variable types
        if (typeof (group.date.year) === 'number'
          && typeof (group.date.month) === 'string'
          && typeof (group.date.day) === 'number') {

          // add dates from group to date range
          dates.push(new Date(group.date.year, this.translateMonthString(group.date.month), group.date.day));
        }
      });
    }

    // sort dates in date range
    dates.sort((a, b) => { return a.getTime() - b.getTime(); });

    // remove duplicate dates
    let uniqueDates = dates
      .map(function (date) { return date.getTime() })
      .filter(function (date, i, array) { return array.indexOf(date) === i })
      .map(function (time) { return new Date(time) });

    // update min and max values
    this.minValue = uniqueDates[0].getTime();
    this.maxValue = uniqueDates[uniqueDates.length - 1].getTime();

    // return date range
    return uniqueDates;
  }

  /**
   * Updates slider range with dates in created date range
   */
  updateSliderRange() {
    this.options = {
      stepsArray: this.dateRange.map((date: Date, index: number) => {
        return { value: date.getTime(), legend: this.getTickLegend(date, index) };
      }),
      translate: (value: number, label: LabelType): string => {
        return this.getDateLabel(new Date(value));
      },
      showTicks: true,
      noSwitching: false,
      ticksTooltip: (v: number): string => {
        return this.getTickTooltip(v);
      }
    };

    // define slider width
    this.sliderWidth = this.dateRange.length * this.sliderTickWidth;

    // slider width min limit
    if (this.sliderWidth < 700) this.sliderWidth = 700;
  }

  /**
   * Updates date range value after user changes minimum date or maximum date in the slider.
   * @param changeContext user changes in slider
   */
  onUserChangeEnd(changeContext: ChangeContext): void {
    if (changeContext.highValue != undefined) {
      // update range dates
      this.minDate = new Date(changeContext.value);
      this.maxDate = new Date(changeContext.highValue);

      // dispatch redux to update range values
      this.dateRangeActions.updateValues(this.minDate, this.maxDate);
    }
  }

  // ------------ helper methods ------------

  /**
   * Translates month name into its number equivalent. Supports language translation.
   * @param monthString month name
   * @returns month value in number format
   */
  translateMonthString(monthString: string): number {
    let month;

    // check language and language switches
    if (this.language === 'pt') {
      month = ptMonths.find(month => month.month === monthString);
      if (month === undefined) month = enMonths.find(month => month.month === monthString);
    }
    else { // language is 'en'
      month = enMonths.find(month => month.month === monthString);
      if (month === undefined) month = ptMonths.find(month => month.month === monthString);
    }

    if (month !== undefined) {
      return month.value;
    }
    return -1;
  }

  /**
   * Gets date labels for date selection in the slider. Supports language translation.
   * @param date date to get the label for
   * @returns label for the selected date
   */
  getDateLabel(date: Date): string {
    // get date values
    let day = date.getDate();
    let month;
    if (this.language === 'pt') month = ptMonths[date.getMonth()].month;
    else month = enMonths[date.getMonth()].month;

    let year = date.getFullYear();

    // return date label
    let label = day + ' ' + month + ' ' + year;
    return label;
  }

  /**
   * Gets month legend for initial month slider ticks. Only adds a month to separate dates from different months.
   * Supports language translation.
   * @param date date to get the month legend for
   * @param index index of date in date range
   * @returns month name if needed, empty otherwise.
   */
  getTickLegend(date: Date, index: number): string {
    // add legend to first date
    if (index === 0) {
      if (this.language === 'pt') return ptMonths[date.getMonth()].month;
      else return enMonths[date.getMonth()].month;
    }

    // if month from date before is different, add month legend
    else if (this.dateRange[index - 1].getMonth() !== this.dateRange[index].getMonth()) {
      if (this.language === 'pt') return ptMonths[date.getMonth()].month;
      else return enMonths[date.getMonth()].month;
    }

    // otherwise, no legend
    return '';
  }

  /**
   * Gets date label for slider tooltip.
   * @param index index in date range
   * @returns label for date in selected index
   */
  getTickTooltip(index: number) {
    let date = this.dateRange[index];
    let tooltip = this.getDateLabel(date);
    return tooltip;
  }

  // drag slider (similar to scroll but scroll is used for zoom)
  /**
   * Method called when user starts a drag movement in the slider.
   * @param e drag event
   * @param el DOM element
   */
  startDragging(e: any, el: any) {
    this.mouseDown = true;
    this.startX = e.pageX - el.offsetLeft;
    this.scrollLeft = el.scrollLeft;
  }
  /**
   * Method called when user stops a drag movement in the slider.
   */
  stopDragging() { this.mouseDown = false; }
  /**
   * Method called when user is dragging the slider.
   * @param e drag event
   * @param el DOM element
   * @returns nothing
   */
  moveEvent(e: any, el: any) {
    e.preventDefault();
    if (!this.mouseDown) {
      return;
    }
    const x = e.pageX - el.offsetLeft;
    const scroll = x - this.startX;
    el.scrollLeft = this.scrollLeft - scroll;
  }

  /**
   * Updates slider tick width. Acts as zoom in the slider.
   * @param e scroll event
   */
  updateSliderZoom(e: any) {
    // zoom in with scroll up, zoom out with scroll down
    this.sliderTickWidth += (e / 10) * -1;

    // define width max limit
    if (this.sliderTickWidth > 100) this.sliderTickWidth = 100;

    // update slider options
    this.updateSliderRange();
  }

}