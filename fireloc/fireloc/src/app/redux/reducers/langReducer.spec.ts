import { LangActions } from "../actions/langActions";
import { INITIAL_STATE_LANG, langReducer, LangState } from "./langReducer";


describe('TS58 Redux LangReducer', () => {
    let initialState: LangState;

    beforeEach(() => {
        initialState = INITIAL_STATE_LANG;
    });

    it('T58.1 should have dispatched language change', () => {
        // expected final state
        let finalState = { language: 'en', };
        // action to be used
        let action = { type: LangActions.CHANGE_LANG, payload: { language: 'en', } };

        // call reducer
        let state = langReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T58.2 should not change state when an unexpected action is dispatched', () => {
        // expected final state
        let finalState = INITIAL_STATE_LANG;
        // action to be used
        let action = { type: '' };

        // call reducer
        let state = langReducer(undefined, action);
        // expectation
        expect(state).toEqual(finalState);
    });
});