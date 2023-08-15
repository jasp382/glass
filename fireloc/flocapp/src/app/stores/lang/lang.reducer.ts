import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";

import { Language } from "src/app/interfaces/language";

import * as fromLangAction from "../lang/lang.actions";

/**
 * Interface used for Language state in Redux. 
 */
export interface LangState {
    /**
     * current language used in the app
     */
    language: Language,
    error: string | ''
}


/**
 * Initial Language state in Redux.
 * Initializes state with portuguese language.
 */

export const langInitialState: LangState = {
    language: {language: 'Português', country: 'pt'},
    error: ''
}


/**
 * Language Reducer.
 * This reducer will be used to update LangState.
 */
const _langReducer = createReducer(
    langInitialState,
    on(fromLangAction.GetLanguageSuccess, (state, { payload }) => ({
        ...state, language: payload, error: ''
    })),
    on(fromLangAction.GetLanguageFail, (state, { error }) => ({
        ...state, error: error
    }))
)

export function langReducer(state = langInitialState, action: Action) {
    return _langReducer(state, action);
}


/**
 * Language Select.
 * Returns parts of the Language Store.
 */

const getLangFeatureState = createFeatureSelector<LangState>(
    'lang'
)

export const getLang = createSelector(
    getLangFeatureState,
    (state: LangState) => state.language
)