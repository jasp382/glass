import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";

import { BasemapsService } from "src/app/serv/leafmap/basemaps.service";
import { LyrsService } from "src/app/serv/leafmap/lyrs.service";

import * as leafActions from './leaf.actions';


@Injectable()
export class LeafmapEffects{
    constructor(
        private actions$: Actions,
        private bmapServ: BasemapsService,
        private lyrServ: LyrsService
    ) { }

    updateBasemap$ = createEffect(()=> this.actions$.pipe(
        ofType(leafActions.leafMapActions.UPDATE_BASEMAP),
        exhaustMap((record:any) => this.bmapServ.getBasemapString(record.payload)
            .pipe(
                map(payload =>
                    leafActions.UpdateBasemapSuccess({payload}),
                    catchError(error=> of(leafActions.UpdateBasemapFail({error})))
                )
            )
        )
    ));

    addMapLayer$ = createEffect(()=> this.actions$.pipe(
        ofType(leafActions.leafMapActions.ADD_WMS),
        exhaustMap((record:any) => this.lyrServ.addNewMapLayer(record.payload)
            .pipe(
                map(payload =>
                    leafActions.AddWMSSuccess({payload}),
                    catchError(error=> of(leafActions.AddWMSFail({error})))
                )
            )
        )
    ));

    addCtbLayer$ = createEffect(()=> this.actions$.pipe(
        ofType(leafActions.leafMapActions.ADD_CTBWMS),
        exhaustMap((record:any) => this.lyrServ.addNewContribLayer(record.payload)
            .pipe(
                map(payload =>
                    leafActions.AddContributionWMSSuccess({payload}),
                    catchError(error=> of(leafActions.AddContributionWMSFail({error})))
                )
            )
        )
    ));
}