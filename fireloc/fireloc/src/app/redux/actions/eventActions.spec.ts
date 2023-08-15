import { NgRedux } from "@angular-redux/store";
import { MockNgRedux } from "@angular-redux/store/testing";
import { Event, ServiceLayer } from "src/app/interfaces/events";
import { EventActions } from "./eventActions";

describe('TS48 Redux EventActions', () => {
    let mockNgRedux: NgRedux<any>;
    let eventActions: EventActions;

    beforeEach(() => {
        MockNgRedux.reset();
        mockNgRedux = MockNgRedux.getInstance();
        eventActions = new EventActions(mockNgRedux);
    });

    it('T48.1 should dispatch add event layer', () => {
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
        // expected action and spy
        const expectedAction = {
            type: EventActions.ADD_EVENT_LAYER,
            payload: {
                layer: layer
            }
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        eventActions.addEventLayer(layer);

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T48.2 should dispatch remove event layer', () => {
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
        // expected action and spy
        const expectedAction = {
            type: EventActions.REMOVE_EVENT_LAYER,
            payload: {
                layer: layer
            }
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        eventActions.removeEventLayer(layer);

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T48.3 should dispatch clear event layers', () => {
        // expected action and spy
        const expectedAction = { type: EventActions.CLEAR_EVENT_LAYERS };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        eventActions.clearEventLayers();

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T48.4 should dispatch add events', () => {
        // expected action and spy
        const expectedAction = {
            type: EventActions.SAVE_EVENTS,
            payload: {
                events: [] as Event[]
            }
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        eventActions.addEvents([] as Event[]);

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T48.5 should dispatch clear events', () => {
        // expected action and spy
        const expectedAction = {
            type: EventActions.REMOVE_EVENTS
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        eventActions.clearEvents();

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

});