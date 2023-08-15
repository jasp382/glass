import { tassign } from "tassign";
import { DateRangeActions } from "../actions/dateRangeActions";

/**
 * Interface used for Date Range state in Redux. 
 */
interface DateRangeState {
    /**
     * minimum date stored for date range
     */
    minDate: Date,
    /**
     * maximum date stored for date range
     */
    maxDate: Date
}

/**
 * @ignore
 */
const dateMonthBeforeToday = new Date();
dateMonthBeforeToday.setMonth(dateMonthBeforeToday.getMonth() - 1);

/**
 * Initial Date Range state in Redux.
 * Initializes state with maximum date as the current day and the minimum date one month before the current day.
 */
const INITIAL_STATE_DATERANGE: DateRangeState = { minDate: dateMonthBeforeToday, maxDate: new Date(), };

/**
 * Redux date range reducer.
 * Checks dispatched action and updates the date range state with provided payload.
 * 
 * See {@link DateRangeActions} for possible actions.
 * @param state Redux Date Range  State. If none provided, initial state is used.
 * @param action dispatched action from redux
 * @returns new date range state
 */
function dateRangeReducer(state: DateRangeState = INITIAL_STATE_DATERANGE, action: any) {
    switch (action.type) {
        // update range values
        case DateRangeActions.UPDATE_RANGE_VALUES:
            return tassign(state, { minDate: action.payload.minDate, maxDate: action.payload.maxDate });
        // remove range values
        case DateRangeActions.REMOVE_RANGE_VALUES:
            return tassign(state, { minDate: new Date(), maxDate: new Date() });
        default: return state;
    }
}

export { DateRangeState, dateRangeReducer, INITIAL_STATE_DATERANGE };