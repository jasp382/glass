import { NgRedux } from "@angular-redux/store";
import { MockNgRedux } from "@angular-redux/store/testing";
import { RealEvent } from "src/app/interfaces/realEvents";
import { RealEventActions } from "./realEventActions";

describe('TS51 Redux RealEventActions', () => {
    let mockNgRedux: NgRedux<any>;
    let realEventActions: RealEventActions;

    beforeEach(() => {
        MockNgRedux.reset();
        mockNgRedux = MockNgRedux.getInstance();
        realEventActions = new RealEventActions(mockNgRedux);
    });

    it('T51.1 should dispatch add real events', () => {
        // expected action and spy
        const expectedAction = {
            type: RealEventActions.SAVE_REAL_EVENTS,
            payload: {
                events: [] as RealEvent[]
            }
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        realEventActions.addRealEvents([] as RealEvent[]);

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T51.2 should dispatch clear real events', () => {
        // expected action and spy
        const expectedAction = {
            type: RealEventActions.CLEAR_REAL_EVENTS
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        realEventActions.clearRealEvents();

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });
});