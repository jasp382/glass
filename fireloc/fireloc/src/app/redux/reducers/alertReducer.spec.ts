import { AlertActions } from "../actions/alertActions";
import { alertReducer, AlertState, INITIAL_STATE_ALERT } from "./alertReducer";

describe('TS53 Redux AlertReducer', () => {
    let initialState: AlertState;

    beforeEach(() => {
        initialState = INITIAL_STATE_ALERT;
    });

    it('T53.1 should have dispatched alert', () => {
        // expected final state
        let finalState = {
            alertMessage: {
                type: 'success',
                message: 'Email enviado! <strong>Verifique o seu email</strong> para recuperar a sua conta.',
            },
            hasAlert: true,
        };
        // action to be used
        let action = {
            type: AlertActions.ADD_ALERT,
            payload: {
                type: 'success',
                message: 'Email enviado! <strong>Verifique o seu email</strong> para recuperar a sua conta.'
            }
        };

        // call reducer
        let state = alertReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T53.2 should reset alert', () => {
        // expected final state
        let finalState = INITIAL_STATE_ALERT;
        // action to be used
        let action = { type: AlertActions.RESET_ALERT };

        // call reducer
        let state = alertReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T53.3 should not change state when an unexpected action is dispatched', () => {
        // expected final state
        let finalState = INITIAL_STATE_ALERT;
        // action to be used
        let action = { type: '' };

        // call reducer
        let state = alertReducer(undefined, action);
        // expectation
        expect(state).toEqual(finalState);
    });
});