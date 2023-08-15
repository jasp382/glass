import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";


import { LayerService } from "src/app/serv/rest/geo/layer.service";


import * as layerActions from './geolyr.actions';


@Injectable()
export class TreeLayerEffects{
    constructor(
        private actions$: Actions,
        private lyrService: LayerService
    ) { }


    getTreeLayers$ = createEffect(()=> this.actions$.pipe(
        ofType(layerActions.treeLayerTypeAction.GET_TREELAYERS),
        exhaustMap((record: any) => this.lyrService.getLayers(
            record.payload.token, record.payload.astree)
            .pipe(
                map(payload =>
                    layerActions.GetTreeLayerSuccess({payload}),
                    catchError(error => of(layerActions.GetTreeLayerFail({error})))
                )
            )
        )
    ));
}