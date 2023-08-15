import { INITIAL_STATE } from ".";
import { INITIAL_STATE_ALERT } from "./alertReducer";
import { INITIAL_STATE_CONTRIB } from "./contributionReducer";
import { INITIAL_STATE_DATERANGE } from "./dateRangeReducer";
import { INITIAL_STATE_EVENT } from "./eventReducer";
import { INITIAL_STATE_LANG } from "./langReducer";
import { INITIAL_STATE_LAYER } from "./layerReducer";
import { INITIAL_STATE_REAL_EVENT } from "./realEventReducer";
import { INITIAL_STATE_USER } from "./userReducer";

describe('TS57 Redux Reducers Index', () => {

    it('T57.1 should correctly define redux state', () => {
        expect(INITIAL_STATE).toEqual({
            alert: INITIAL_STATE_ALERT,
            contribution: INITIAL_STATE_CONTRIB,
            event: INITIAL_STATE_EVENT,
            realEvent: INITIAL_STATE_REAL_EVENT,
            user: INITIAL_STATE_USER,
            dateRange: INITIAL_STATE_DATERANGE,
            layer: INITIAL_STATE_LAYER,
            language: INITIAL_STATE_LANG
        });
    });
});