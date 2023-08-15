import { RealEvent } from "src/app/interfaces/realEvents";
import { RealEventActions } from "../actions/realEventActions";
import { INITIAL_STATE_REAL_EVENT, realEventReducer, RealEventState } from "./realEventReducer";

describe('TS60 Redux RealEventReducer', () => {
    let initialState: RealEventState;

    beforeEach(() => {
        initialState = INITIAL_STATE_REAL_EVENT;
    });

    it('T60.1 should add real events', () => {
        // expected final state
        let finalState = { events: [] };
        // action to be used
        let action = {
            type: RealEventActions.SAVE_REAL_EVENTS,
            payload: {
                events: [] as RealEvent[]
            }
        };

        // call reducer
        let state = realEventReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T60.2 should clear real events', () => {
        // expected final state
        let finalState = { events: [] };
        // action to be used
        let action = { type: RealEventActions.CLEAR_REAL_EVENTS };

        // call reducer
        let state = realEventReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T60.3 should not change state when an unexpected action is dispatched', () => {
        // expected final state
        let finalState = INITIAL_STATE_REAL_EVENT;
        // action to be used
        let action = { type: '' };

        // call reducer
        let state = realEventReducer(undefined, action);
        // expectation
        expect(state).toEqual(finalState);
    });
});