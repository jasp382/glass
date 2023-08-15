import { DateRangeActions } from "../actions/dateRangeActions";
import { dateRangeReducer, DateRangeState, INITIAL_STATE_DATERANGE } from "./dateRangeReducer";

describe('TS55 Redux DateRangeReducer', () => {
    let initialState: DateRangeState;

    beforeEach(() => {
        initialState = INITIAL_STATE_DATERANGE;
    });

    afterEach(function () {
        jasmine.clock().uninstall();
    });

    it('T55.1 should update values', () => {
        // expected final state
        let finalState = {
            minDate: new Date(1),
            maxDate: new Date(2),
        };
        // action to be used
        let action = {
            type: DateRangeActions.UPDATE_RANGE_VALUES,
            payload: {
                minDate: new Date(1),
                maxDate: new Date(2),
            }
        };

        // call reducer
        let state = dateRangeReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T55.2 should clear values', () => {
        jasmine.clock().install();
        var baseTime = new Date(100);
        jasmine.clock().mockDate(baseTime);

        // expected final state
        let finalState = {
            minDate: baseTime,
            maxDate: baseTime,
        };
        // action to be used
        let action = {
            type: DateRangeActions.REMOVE_RANGE_VALUES,
        };

        // call reducer
        let state = dateRangeReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T55.3 should not change state when an unexpected action is dispatched', () => {
        // expected final state
        let finalState = INITIAL_STATE_DATERANGE;
        // action to be used
        let action = { type: '' };

        // call reducer
        let state = dateRangeReducer(undefined, action);
        // expectation
        expect(state).toEqual(finalState);
    });
});