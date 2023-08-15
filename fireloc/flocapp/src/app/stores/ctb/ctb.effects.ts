import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";

import { CtbService } from "src/app/serv/rest/ctb.service";

import * as ctbActions from './ctb.actions';


@Injectable()
export class ContribEffects{
    constructor(
        private actions$: Actions,
        private ctbService: CtbService
    ) { }

    getAllContrib$ = createEffect(()=> this.actions$.pipe(
        ofType(ctbActions.ctbTypeAction.GET_CONTRIBS),
        exhaustMap((record: any) => this.ctbService.getContribByDay(record.payload)
            .pipe(
                map(payload =>
                    ctbActions.GetContribsSuccess({payload}),
                    catchError(error => of(ctbActions.GetContribsFail({error})))
                )
            )
        )
    ));

    getUserContrib$ = createEffect(()=> this.actions$.pipe(
        ofType(ctbActions.ctbTypeAction.GET_USER_CONTRIBS),
        exhaustMap((record: any) => this.ctbService.getContributions(
            record.payload.token, record.payload.userid
            ).pipe(
                map(payload =>
                    ctbActions.GetUserContribsSuccess({payload}),
                    catchError(error => of(ctbActions.GetUserContribsFail({error})))
                )
            )
        )
    ));

    getGeoContrib$ = createEffect(()=> this.actions$.pipe(
        ofType(ctbActions.ctbTypeAction.GET_GEO_CONTRIBS),
        exhaustMap((record: any) => this.ctbService.getContributions(
            record.payload.token, undefined, undefined, undefined, undefined,
            record.payload.fgeom
            ).pipe(
                map(payload =>
                    ctbActions.GetGeoContribsSuccess({payload}),
                    catchError(error => of(ctbActions.GetGeoContribsFail({error})))
                )
            )
        )
    ));

    getContribTable$ = createEffect(() => this.actions$.pipe(
        ofType(ctbActions.ctbTypeAction.GET_CONTRIBS_TABLE),
        exhaustMap((record: any) => this.ctbService.getContributions(
            record.payload.token, record.payload.strips
            ).pipe(
                map(payload =>
                    ctbActions.GetContribsTableSuccess({payload}),
                    catchError(error => of(ctbActions.GetContribsTableFail({error})))
                )
            )
        )
    ));

    getContribPhoto$ = createEffect(() => this.actions$.pipe(
        ofType(ctbActions.ctbTypeAction.GET_CONTRIB_PHOTO),
        exhaustMap((record: any) => this.ctbService.getContributionPhoto(
            record.payload.token, record.payload.photo
            ).pipe(
                map(payload =>
                    ctbActions.GetContribPhotoSuccess({payload}),
                    catchError(error => of(ctbActions.GetContribPhotoFail({error})))
                )
            )
        )
    ));
}