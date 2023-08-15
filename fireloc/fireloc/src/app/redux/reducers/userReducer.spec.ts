import { UserActions } from "../actions/userActions";
import { INITIAL_STATE_USER, userReducer, UserState } from "./userReducer";

describe('TS61 Redux UserReducer', () => {
    let initialState: UserState;

    beforeEach(() => {
        initialState = INITIAL_STATE_USER;
    });

    it('T61.1 should perform user info action', () => {
        // expected final state
        let finalState = INITIAL_STATE_USER;
        // action to be used
        let action = { type: UserActions.GET_USER_INFO };

        // call reducer
        let state = userReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T61.2 should not change state when an unexpected action is dispatched', () => {
        // expected final state
        let finalState = INITIAL_STATE_USER;
        // action to be used
        let action = { type: '' };

        // call reducer
        let state = userReducer(undefined, action);
        // expectation
        expect(state).toEqual(finalState);
    });
});