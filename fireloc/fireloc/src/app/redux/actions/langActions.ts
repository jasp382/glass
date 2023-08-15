import { Injectable } from '@angular/core';
import { NgRedux } from '@angular-redux/store';
import { AppState } from '../reducers';

/**
 * Redux language actions. 
 * These actions are meant to be dispatched and caught by {@link langReducer}.
 */
@Injectable()
export class LangActions {

    /**
     * Action to switch app language in redux state
     */
    static CHANGE_LANG = 'CHANGE_LANG';

    /**
     * Empty constructor
     * @param ngRedux Redux to dispatch actions
     */
    constructor(private ngRedux: NgRedux<AppState>) { }

    // change app language
    /**
     * Dispatch action to change the language stored in redux state
     * @param language 
     */
    changeLanguage(language: string) {
        this.ngRedux.dispatch({ type: LangActions.CHANGE_LANG, payload: { language: language } });
    }
}