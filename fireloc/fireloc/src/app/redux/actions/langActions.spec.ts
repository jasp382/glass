import { NgRedux } from "@angular-redux/store";
import { MockNgRedux } from "@angular-redux/store/testing";
import { LangActions } from "./langActions";

describe('TS49 Redux LangActions', () => {
    let mockNgRedux: NgRedux<any>;
    let langActions: LangActions;

    beforeEach(() => {
        MockNgRedux.reset();
        mockNgRedux = MockNgRedux.getInstance();
        langActions = new LangActions(mockNgRedux);
    });

    it('T49.1 should dispatch change language action', () => {
        // expected action and spy
        const expectedAction = { type: LangActions.CHANGE_LANG, payload: { language: 'en', } };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        langActions.changeLanguage('en');

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });
});