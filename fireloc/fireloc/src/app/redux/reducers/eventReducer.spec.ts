import { Event, ServiceLayer } from "src/app/interfaces/events";
import { EventActions } from "../actions/eventActions";
import { eventReducer, EventState, INITIAL_STATE_EVENT } from "./eventReducer";

describe('TS56 Redux EventReducer', () => {
    let initialState: EventState;

    beforeEach(() => {
        initialState = INITIAL_STATE_EVENT;
    });

    it('T56.1 should add event layer', () => {
        // fake data
        let layer: ServiceLayer = {
            id: 0,
            gLayer: "g",
            slug: "s",
            store: "s",
            style: "s",
            work: "w",
            design: "d"
        }
        // expected final state
        let finalState = { serviceLayers: [layer], events: [], };
        // action to be used
        let action = {
            type: EventActions.ADD_EVENT_LAYER,
            payload: {
                layer: layer
            }
        };

        // call reducer
        let state = eventReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T56.2 should remove event layer', () => {
        // fake data
        let layer: ServiceLayer = {
            id: 0,
            gLayer: "g",
            slug: "s",
            store: "s",
            style: "s",
            work: "w",
            design: "d"
        }
        initialState = { serviceLayers: [layer], events: [], }
        // expected final state
        let finalState = {
            serviceLayers: [],
            events: [],
        };
        // action to be used
        let action = {
            type: EventActions.REMOVE_EVENT_LAYER,
            payload: {
                layer: layer
            }
        };

        // call reducer
        let state = eventReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T56.3 should clear event layers', () => {
        // expected final state
        let finalState = { serviceLayers: [], events: [], };
        // action to be used
        let action = { type: EventActions.CLEAR_EVENT_LAYERS, };

        // call reducer
        let state = eventReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T56.4 should save events', () => {
        // expected final state
        let finalState = { serviceLayers: [], events: [], };
        // action to be used
        let action = {
            type: EventActions.SAVE_EVENTS,
            payload: {
                events: [] as Event[]
            }
        };

        // call reducer
        let state = eventReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T56.5 should clear events', () => {
        // expected final state
        let finalState = { serviceLayers: [], events: [], };
        // action to be used
        let action = { type: EventActions.REMOVE_EVENTS, };

        // call reducer
        let state = eventReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T56.6 should not change state when an unexpected action is dispatched', () => {
        // expected final state
        let finalState = INITIAL_STATE_EVENT;
        // action to be used
        let action = { type: '' };

        // call reducer
        let state = eventReducer(undefined, action);
        // expectation
        expect(state).toEqual(finalState);
    });
});