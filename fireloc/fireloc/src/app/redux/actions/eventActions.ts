import { Injectable } from '@angular/core';
import { NgRedux } from '@angular-redux/store';
import { AppState } from '../reducers';
import { Event, ServiceLayer } from 'src/app/interfaces/events';

/**
 * Redux events actions. 
 * These actions are meant to be dispatched and caught by {@link eventReducer}.
 */
@Injectable()
export class EventActions {
    /**
     * Action to add an event service layer
     */
    static ADD_EVENT_LAYER = 'ADD_EVENT_LAYER';
    /**
     * Action to remove a stored event service layer
     */
    static REMOVE_EVENT_LAYER = 'REMOVE_EVENT_LAYER';
    /**
     * Action to clear all event service layers
     */
    static CLEAR_EVENT_LAYERS = 'CLEAR_EVENT_LAYERS';

    /**
     * Action to save events in redux state
     */
    static SAVE_EVENTS = 'SAVE_EVENTS';
    /**
     * Action to remove all stored events in redux state
     */
    static REMOVE_EVENTS = 'REMOVE_EVENTS';

    /**
     * Empty constructor
     * @param ngRedux Redux to dispatch actions
     */
    constructor(private ngRedux: NgRedux<AppState>) { }

    /**
     * Dispatch action to add an event service layer in redux state
     * @param layer event service layer to be added
     */
    addEventLayer(layer: ServiceLayer) {
        this.ngRedux.dispatch({ type: EventActions.ADD_EVENT_LAYER, payload: { layer: layer } });
    }

    /**
     * Dispatch action to remove an event service layer stored in redux state
     * @param layer 
     */
    removeEventLayer(layer: ServiceLayer) {
        this.ngRedux.dispatch({ type: EventActions.REMOVE_EVENT_LAYER, payload: { layer: layer } });
    }

    /**
     * Dispatch action to clear all event service layers stored in redux state
     */
    clearEventLayers() {
        this.ngRedux.dispatch({ type: EventActions.CLEAR_EVENT_LAYERS });
    }

    /**
     * Dispatch action to store list of events in redux state
     * @param events events to store in redux state
     */
    addEvents(events: Event[]) {
        this.ngRedux.dispatch({ type: EventActions.SAVE_EVENTS, payload: { events: events } });
    }

    /**
     * Dispatch action to clear all events stored in redux state
     */
    clearEvents() {
        this.ngRedux.dispatch({ type: EventActions.REMOVE_EVENTS });
    }

}