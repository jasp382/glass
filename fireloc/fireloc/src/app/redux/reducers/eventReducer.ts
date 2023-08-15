import { tassign } from "tassign";
import { EventActions } from "../actions/eventActions";
import { Event, ServiceLayer } from "src/app/interfaces/events";

/**
 * Interface used for Event state in Redux. 
 */
interface EventState {
    /**
     * list of event service layers stored
     */
    serviceLayers: ServiceLayer[],
    /**
     * list of events stored
     */
    events: Event[],
}

/**
 * Initial Event state in Redux.
 * Initializes state with empty lists.
 */
const INITIAL_STATE_EVENT: EventState = { serviceLayers: [], events: [], };

/**
 * Redux event reducer.
 * Checks dispatched action and updates the event state with provided payload.
 * 
 * See {@link EventActions} for possible actions.
 * @param state Redux Event State. If none provided, initial state is used.
 * @param action dispatched action from redux
 * @returns new event state
 */
function eventReducer(state: EventState = INITIAL_STATE_EVENT, action: any) {
    switch (action.type) {
        // add event layer
        case EventActions.ADD_EVENT_LAYER:
            return tassign(state, { serviceLayers: [...state.serviceLayers, action.payload.layer] });
        // remove event layer
        case EventActions.REMOVE_EVENT_LAYER:
            return tassign(state, { serviceLayers: state.serviceLayers.filter(layer => layer !== action.payload.layer) });
        // clear all event layers
        case EventActions.CLEAR_EVENT_LAYERS:
            return tassign(state, { serviceLayers: <ServiceLayer[]>[], });
        // save events
        case EventActions.SAVE_EVENTS:
            return tassign(state, { events: action.payload.events, });
        // remove events from redux
        case EventActions.REMOVE_EVENTS:
            return tassign(state, { events: <Event[]>[], });
        default: return state;
    }
}

export { EventState, eventReducer, INITIAL_STATE_EVENT };