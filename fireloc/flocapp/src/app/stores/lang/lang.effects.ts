import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";

import { LangService } from "src/app/serv/lang.service";
import * as fromLangAction from './lang.actions';



@Injectable()
export class LangEffects{
    constructor(
        private actions$: Actions,
        private langService: LangService
    ) { }

    getLang$ = createEffect(()=> this.actions$.pipe(
        ofType(fromLangAction.langTypeAction.GET_LANG),
        exhaustMap((record: any) => this.langService.getLanguage(record.payload)
            .pipe(
                map(payload =>
                    fromLangAction.GetLanguageSuccess({payload}),
                    catchError(error => of(fromLangAction.GetLanguageFail({error})))
                )
            )
        )
    ))
}