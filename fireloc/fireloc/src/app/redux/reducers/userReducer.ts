import { tassign } from "tassign";
import { UserActions } from "../actions/userActions";

/**
 * Interface used for User state in Redux. 
 * Empty due to not needing information in app, information is provided by API. 
 * State is used to coordinate when UI needs to get updated information.
 */
interface UserState { }

/**
 * Initial User state in Redux
 * Empty due to not needing information in app, information is provided by API. 
 * State is used to coordinate when UI needs to get updated information.
 */
const INITIAL_STATE_USER: UserState = {};

/**
 * Redux user reducer. Checks dispatched action and updates the state.
 * 
 * See {@link UserActions} for possible actions.
 * @param state Redux User State. If none provided, initial state is used.
 * @param action dispatched action from redux
 * @returns new user state
 */
function userReducer(state: UserState = INITIAL_STATE_USER, action: any) {
    switch (action.type) {
        case UserActions.GET_USER_INFO: return tassign(state, state);
        default: return state;
    }
}

export { UserState, userReducer, INITIAL_STATE_USER };