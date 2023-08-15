import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";

import { GeosrvService } from "src/app/serv/rest/geosrv.service";

import * as cLayerActions from './clyr.actions';


@Injectable()
export class ClusterLayerEffects {
    constructor(
        private actions$: Actions,
        private lyrService: GeosrvService
    ) { }


    getClusterLayers$ = createEffect(()=> this.actions$.pipe(
        ofType(cLayerActions.clusterLayerTypeAction.GET_CLUSTERLYR),
        exhaustMap((record: any) => this.lyrService.getClusterLayers(record.payload)
            .pipe(
                map(payload =>
                    cLayerActions.GetClusterLayerSuccess({payload}),
                    catchError(error => of(cLayerActions.GetClusterLayerFail({error})))
                )
            )
        )
    ));

    getClusterWFS$ = createEffect(()=> this.actions$.pipe(
        ofType(cLayerActions.clusterLayerTypeAction.CLUSTER_WFS),
        exhaustMap((record: any) => this.lyrService.getWFS(
            record.payload.token, record.payload.ws, record.payload.lyr)
            .pipe(
                map(payload =>
                    cLayerActions.ClusterWFSSuccess({payload}),
                    catchError(error => of(cLayerActions.ClusterWFSFail({error})))
                )
            )
        )
    ));

    getClusterWFSBBOX$ = createEffect(()=> this.actions$.pipe(
        ofType(cLayerActions.clusterLayerTypeAction.CLUSTER_WFSBBOX),
        exhaustMap((record: any) => this.lyrService.getWFS(
            record.payload.token, record.payload.ws, record.payload.lyr, record.payload.bbox)
            .pipe(
                map(payload =>
                    cLayerActions.ClusterWFSBBOXSuccess({payload}),
                    catchError(error => of(cLayerActions.ClusterWFSBBOXFail({error})))
                )
            )
        )
    ));

    clusterToActivate$ = createEffect(()=> this.actions$.pipe(
        ofType(cLayerActions.clusterLayerTypeAction.ID_CLUSTER),
        exhaustMap((record: any) => this.lyrService.clusterLayerIsActive(record.payload)
            .pipe(
                map(payload =>
                    cLayerActions.IdClusterSuccess({payload}),
                    catchError(error => of(cLayerActions.IdClusterFail({error})))
                )
            )
        )
    ));

    showClusterLayer$ = createEffect(()=> this.actions$.pipe(
        ofType(cLayerActions.clusterLayerTypeAction.SHOW_CLUSTER),
        exhaustMap((record: any) => this.lyrService.mainLayerActiveStatus(record.payload)
            .pipe(
                map(payload =>
                    cLayerActions.ShowStatusSuccess({payload}),
                    catchError(error => of(cLayerActions.ShowStatusFail({error})))
                )
            )
        )
    ));
}