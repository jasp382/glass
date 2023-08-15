import { combineReducers } from "redux";

// reducers and initial states
import { alertReducer, AlertState, INITIAL_STATE_ALERT } from "./alertReducer";
import { contributionReducer, ContributionState, INITIAL_STATE_CONTRIB } from "./contributionReducer";
import { dateRangeReducer, DateRangeState, INITIAL_STATE_DATERANGE } from "./dateRangeReducer";
import { eventReducer, EventState, INITIAL_STATE_EVENT } from "./eventReducer";
import { INITIAL_STATE_REAL_EVENT, realEventReducer, RealEventState } from "./realEventReducer";
import { INITIAL_STATE_LAYER, layerReducer, LayerState } from "./layerReducer";
import { INITIAL_STATE_USER, userReducer, UserState } from "./userReducer";
import { INITIAL_STATE_LANG, langReducer, LangState } from "./langReducer";

/**
 * Redux Root Reducer. Combines all existing redux reducers.
 */
const rootReducer = combineReducers({
    alert: alertReducer,
    contribution: contributionReducer,
    event: eventReducer,
    realEvent: realEventReducer,
    user: userReducer,
    dateRange: dateRangeReducer,
    layer: layerReducer,
    language: langReducer
});

/**
 * Redux App State. Combines all existing redux states.
 */
interface AppState {
    /**
     * Alert state. See {@link AlertState}.
     */
    alert: AlertState,
    /**
     * Contribution state. See {@link ContributionState}.
     */
    contribution: ContributionState,
    /**
     * Event state. See {@link EventState}.
     */
    event: EventState,
    /**
     * Real Event state. See {@link RealEventState}.
     */
    realEvent: RealEventState,
    /**
     * User state. See {@link UserState}.
     */
    user: UserState,
    /**
     * Date Range state. See {@link DateRangeState}.
     */
    dateRange: DateRangeState,
    /**
     * Layer state. See {@link LayerState}.
     */
    layer: LayerState,
    /**
     * Language state. See {@link LangState}.
     */
    language: LangState
}

/**
 * Redux initial state. Combines all existing initial redux states.
 */
const INITIAL_STATE = {
    alert: INITIAL_STATE_ALERT,
    contribution: INITIAL_STATE_CONTRIB,
    event: INITIAL_STATE_EVENT,
    realEvent: INITIAL_STATE_REAL_EVENT,
    user: INITIAL_STATE_USER,
    dateRange: INITIAL_STATE_DATERANGE,
    layer: INITIAL_STATE_LAYER,
    language: INITIAL_STATE_LANG
}

export { rootReducer, AppState, INITIAL_STATE };