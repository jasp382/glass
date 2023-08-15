import { tassign } from "tassign";
import { RealEventActions } from "../actions/realEventActions";
import { RealEvent } from "src/app/interfaces/realEvents";

/**
 * Interface used for Real Event state in Redux. 
 */
interface RealEventState {
    /**
     * list of real events stored
     */
    events: RealEvent[]
}

/**
 * Initial Real Event state in Redux.
 * Initializes state with empty list.
 */
const INITIAL_STATE_REAL_EVENT: RealEventState = { events: [] };

/**
 * Redux real event reducer. 
 * Checks dispatched action and updates the real event state with provided payload.
 * 
 * See {@link RealEventActions} for possible actions.
 * @param state Redux Real Event State. If none provided, initial state is used.
 * @param action dispatched action from redux
 * @returns new real event state
 */
function realEventReducer(state: RealEventState = INITIAL_STATE_REAL_EVENT, action: any) {
    switch (action.type) {
        // save real events
        case RealEventActions.SAVE_REAL_EVENTS: return tassign(state, { events: action.payload.events, });
        // remove real events from redux
        case RealEventActions.CLEAR_REAL_EVENTS: return tassign(state, { events: <RealEvent[]>[], });
        default: return state;
    }
}

export { RealEventState, realEventReducer, INITIAL_STATE_REAL_EVENT };