import { tassign } from "tassign";
import { AlertActions } from "../actions/alertActions";

/**
 * Interface used for Alert state in Redux. 
 */
interface AlertState {
    /**
     * alert type and message stored
     */
    alertMessage: {
        type: any,
        message: any
    },
    /**
     * flag for having an alert
     */
    hasAlert: boolean,
}

/**
 * Initial Alert state in Redux.
 * Initializes state with empty values for the alert and false for having an alert.
 */
const INITIAL_STATE_ALERT: AlertState = { alertMessage: { type: '', message: '' }, hasAlert: false };

/**
 * Redux alert reducer.
 * Checks dispatched action and updates the alert state with provided payload.
 * 
 * See {@link AlertActions} for possible actions.
 * @param state Redux Alert State. If none provided, initial state is used.
 * @param action dispatched action from redux
 * @returns new alert state
 */
function alertReducer(state: AlertState = INITIAL_STATE_ALERT, action: any) {
    switch (action.type) {
        // add new alert
        case AlertActions.ADD_ALERT:
            return tassign(state, { alertMessage: { type: action.payload.type, message: action.payload.message }, hasAlert: true });
        // reset alert
        case AlertActions.RESET_ALERT:
            return tassign(state, { alertMessage: { type: '', message: '' }, hasAlert: false });
        default: return state;
    }
}

export { AlertState, alertReducer, INITIAL_STATE_ALERT };