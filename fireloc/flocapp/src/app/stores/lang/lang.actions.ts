import { createAction, props } from "@ngrx/store";

import { Language } from "src/app/interfaces/language";


export const enum langTypeAction {
    GET_LANG         = '[GET_LANG] GET LANGUAGE',
    GET_LANG_SUCCESS = '[GET_LANG_SUCCESS] GET LANGUAGE SUCCESS',
    GET_LANG_FAIL    = '[GET_LANG_FAIL] GET LANGUAGE FAIL'
}

export const GetLanguage = createAction(
    langTypeAction.GET_LANG,
    props<{ payload: Language }>()
)

export const GetLanguageSuccess = createAction(
    langTypeAction.GET_LANG_SUCCESS,
    props<{ payload: Language }>()
)

export const GetLanguageFail = createAction(
    langTypeAction.GET_LANG_FAIL,
    props<{ error: string}>()
)