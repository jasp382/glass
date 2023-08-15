import { Injectable } from '@angular/core';
import { NgRedux } from '@angular-redux/store';
import { AppState } from '../reducers';

/**
 * Redux date range actions. 
 * These actions are meant to be dispatched and caught by {@link dateRangeReducer}.
 */
@Injectable()
export class DateRangeActions {
    /**
     * Action to update date range values
     */
    static UPDATE_RANGE_VALUES = 'UPDATE_RANGE_VALUES';
    /**
     * Action do reset date range values
     */
    static REMOVE_RANGE_VALUES = 'REMOVE_RANGE_VALUES';

    /**
     * Empty constructor
     * @param ngRedux Redux to dispatch actions
     */
    constructor(private ngRedux: NgRedux<AppState>) { }

    /**
     * Dispatch action to update date range stored in redux state
     * @param minDate new minimum date range date
     * @param maxDate new maximum date range date
     */
    updateValues(minDate: Date, maxDate: Date) {
        this.ngRedux.dispatch({ type: DateRangeActions.UPDATE_RANGE_VALUES, payload: { minDate: minDate, maxDate: maxDate, } });
    }

    /**
     * Dispatch action to reset date range stored in redux state
     */
    removeValues() {
        this.ngRedux.dispatch({ type: DateRangeActions.REMOVE_RANGE_VALUES });
    }
}