import { Injectable } from '@angular/core';
import { NgRedux } from '@angular-redux/store';
import { AppState } from '../reducers';
import { RealEvent } from 'src/app/interfaces/realEvents';

/**
 * Redux alert actions. 
 * These actions are meant to be dispatched and caught by {@link realEventReducer}.
 */
@Injectable()
export class RealEventActions {

    /**
     * Action to store real events in redux state
     */
    static SAVE_REAL_EVENTS = 'SAVE_REAL_EVENTS';
    /**
     * Action to clear stored real events in redux state
     */
    static CLEAR_REAL_EVENTS = 'CLEAR_REAL_EVENTS';

    /**
     * Empty constructor
     * @param ngRedux Redux to dispatch actions
     */
    constructor(private ngRedux: NgRedux<AppState>) { }

    /**
     * Dispatch action to store real events in redux state
     * @param events list if events to store
     */
    addRealEvents(events: RealEvent[]) {
        this.ngRedux.dispatch({ type: RealEventActions.SAVE_REAL_EVENTS, payload: { events: events } });
    }

    /**
     * Dispatch action to clear stored real events
     */
    clearRealEvents() {
        this.ngRedux.dispatch({ type: RealEventActions.CLEAR_REAL_EVENTS });
    }

}