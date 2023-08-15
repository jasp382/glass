import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";

import { FlocsService } from "src/app/serv/rest/flocs.service";

import * as firelocActions from './flocs.actions';


@Injectable()
export class FirelocEffects{
    constructor(
        private actions$: Actions,
        private flocService: FlocsService
    ) { }

    getFireloc$ = createEffect(()=> this.actions$.pipe(
        ofType(firelocActions.firelocTypeAction.GET_FIRELOC),
        exhaustMap((record: any) => this.flocService.getFirelocs(
            record.payload.token, record.payload.step)
            .pipe(
                map(payload =>
                    firelocActions.GetFirelocSuccess({payload}),
                    catchError(error => of(firelocActions.GetFirelocFail({error})))
                )
            )
        )
    ));

    getAllFireloc$ = createEffect(()=> this.actions$.pipe(
        ofType(firelocActions.firelocTypeAction.ALL_FIRELOC),
        exhaustMap((record: any) => this.flocService.getFirelocs(record.payload)
            .pipe(
                map(payload =>
                    firelocActions.GetAllFirelocSuccess({payload}),
                    catchError(error => of(firelocActions.GetAllFirelocFail({error})))
                )
            )
        )
    ));
}