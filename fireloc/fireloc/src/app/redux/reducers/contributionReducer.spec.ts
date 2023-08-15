import { ContributionActions } from "../actions/contributionActions";
import { contributionReducer, ContributionState, INITIAL_STATE_CONTRIB } from "./contributionReducer";

describe('TS54 Redux ContributionReducer', () => {
    let initialState: ContributionState;

    beforeEach(() => {
        initialState = INITIAL_STATE_CONTRIB;
    });

    it('T54.1 should save all contributions', () => {
        // expected final state
        let finalState = {
            allContributions: ['test', 'test2'] as any[],
            userContributions: [],
        };
        // action to be used
        let action = {
            type: ContributionActions.SAVE_ALL_CONTRIBS,
            payload: {
                contribs: ['test', 'test2'] as any[]
            }
        };

        // call reducer
        let state = contributionReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T54.2 should save user contributions', () => {
        // expected final state
        let finalState = {
            allContributions: [],
            userContributions: ['test', 'test2'] as any[],
        };
        // action to be used
        let action = {
            type: ContributionActions.SAVE_USER_CONTRIBS,
            payload: {
                contribs: ['test', 'test2'] as any[]
            }
        };

        // call reducer
        let state = contributionReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T54.3 should clear all contributions', () => {
        // expected final state
        let finalState = {
            allContributions: [],
            userContributions: [],
        };
        // action to be used
        let action = { type: ContributionActions.REMOVE_ALL_CONTRIBS, };

        // call reducer
        let state = contributionReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T54.4 should clear user contributions', () => {
        // expected final state
        let finalState = {
            allContributions: [],
            userContributions: [],
        };
        // action to be used
        let action = { type: ContributionActions.REMOVE_USER_CONTRIBS, };

        // call reducer
        let state = contributionReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T54.5 should not change state when an unexpected action is dispatched', () => {
        // expected final state
        let finalState = INITIAL_STATE_CONTRIB;
        // action to be used
        let action = { type: '' };

        // call reducer
        let state = contributionReducer(undefined, action);
        // expectation
        expect(state).toEqual(finalState);
    });
});