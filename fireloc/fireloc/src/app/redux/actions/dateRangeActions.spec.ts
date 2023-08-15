import { NgRedux } from "@angular-redux/store";
import { MockNgRedux } from "@angular-redux/store/testing";
import { DateRangeActions } from "./dateRangeActions";

describe('TS47 Redux DateRangeActions', () => {
    let mockNgRedux: NgRedux<any>;
    let dateRangeActions: DateRangeActions;

    beforeEach(() => {
        MockNgRedux.reset();
        mockNgRedux = MockNgRedux.getInstance();
        dateRangeActions = new DateRangeActions(mockNgRedux);
    });

    it('T47.1 should dispatch update values', () => {
        // expected action and spy
        const expectedAction = {
            type: DateRangeActions.UPDATE_RANGE_VALUES,
            payload: {
                minDate: new Date(1),
                maxDate: new Date(2),
            }
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        dateRangeActions.updateValues(new Date(1), new Date(2));

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T47.2 should dispatch remove values', () => {
        // expected action and spy
        const expectedAction = { type: DateRangeActions.REMOVE_RANGE_VALUES };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        dateRangeActions.removeValues();

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });
});