import { Injectable } from '@angular/core';
import { NgRedux } from '@angular-redux/store';
import { AppState } from '../reducers';
import { ContributionDateGroup } from 'src/app/interfaces/contribs';

/**
 * Redux contribution actions. 
 * These actions are meant to be dispatched and caught by {@link contributionReducer}.
 */
@Injectable()
export class ContributionActions {
    /**
     * Action to store all contributions in redux state
     */
    static SAVE_ALL_CONTRIBS = 'SAVE_ALL_CONTRIBS';
    /**
     * Action to store user contributions in redux state
     */
    static SAVE_USER_CONTRIBS = 'SAVE_USER_CONTRIBS';

    /**
     * Action to clear all contributions stored in redux state
     */
    static REMOVE_ALL_CONTRIBS = 'REMOVE_ALL_CONTRIBS';
    /**
     * Action to clear user contributions stored in redux state
     */
    static REMOVE_USER_CONTRIBS = 'REMOVE_USER_CONTRIBS';

    /**
     * Empty constructor
     * @param ngRedux Redux to dispatch actions
     */
    constructor(private ngRedux: NgRedux<AppState>) { }

    /**
     * Dispatch action to store all contributions in redux state
     * @param contributionGroups contributions to store
     */
    saveAllContributions(contributionGroups: ContributionDateGroup[]) {
        this.ngRedux.dispatch({ type: ContributionActions.SAVE_ALL_CONTRIBS, payload: { contribs: contributionGroups } });
    }

    /**
     * Dispatch action to store user contributions in redux state
     * @param contributionGroups contributions to store
     */
    saveUserContributions(contributionGroups: ContributionDateGroup[]) {
        this.ngRedux.dispatch({ type: ContributionActions.SAVE_USER_CONTRIBS, payload: { contribs: contributionGroups } });
    }

    /**
     * Dispatch action to clear all contributions stored in redux state
     */
    removeAllContributions() {
        this.ngRedux.dispatch({ type: ContributionActions.REMOVE_ALL_CONTRIBS });
    }

    /**
     * Dispatch action to clear user contributions stored in redux state
     */
    removeUserContributions() {
        this.ngRedux.dispatch({ type: ContributionActions.REMOVE_USER_CONTRIBS });
    }
}