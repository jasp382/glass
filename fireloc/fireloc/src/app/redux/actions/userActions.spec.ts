import { NgRedux } from "@angular-redux/store";
import { MockNgRedux } from "@angular-redux/store/testing";
import { UserActions } from "./userActions";

describe('TS52 Redux UserActions', () => {
    let mockNgRedux: NgRedux<any>;
    let userActions: UserActions;

    beforeEach(() => {
        MockNgRedux.reset();
        mockNgRedux = MockNgRedux.getInstance();
        userActions = new UserActions(mockNgRedux);
    });

    it('T52.1 should dispatch get user info', () => {
        // expected action and spy
        const expectedAction = {
            type: UserActions.GET_USER_INFO         
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        userActions.getUserInfo();

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });
});