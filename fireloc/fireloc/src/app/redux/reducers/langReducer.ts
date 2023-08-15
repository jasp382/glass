import { tassign } from "tassign";
import { LangActions } from "../actions/langActions";

/**
 * Interface used for Language state in Redux. 
 */
interface LangState {
    /**
     * current language used in the app
     */
    language: string
}

/**
 * Initial Language state in Redux.
 * Initializes state with portuguese language.
 */
const INITIAL_STATE_LANG: LangState = { language: 'pt' };

/**
 * Redux language reducer.
 * Checks dispatched action and updates the language state with provided payload.
 * 
 * See {@link LangActions} for possible actions.
 * @param state Redux Language State. If none provided, initial state is used.
 * @param action dispatched action from redux
 * @returns new language state
 */
function langReducer(state: LangState = INITIAL_STATE_LANG, action: any) {
    switch (action.type) {
        // change app language
        case LangActions.CHANGE_LANG: return tassign(state, { language: action.payload.language });
        default: return state;
    }
}

export { LangState, langReducer, INITIAL_STATE_LANG };