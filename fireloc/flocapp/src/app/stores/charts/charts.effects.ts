import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";

import { ChartService } from "src/app/serv/rest/chart.service";

import * as chartActions from './charts.actions';


@Injectable()
export class ChartsEffects{
    constructor(
        private actions$: Actions,
        private chartService: ChartService
    ) { }

    getCharts$ = createEffect(()=> this.actions$.pipe(
        ofType(chartActions.chartTypeAction.GET_CHARTS),
        exhaustMap((record: any) => this.chartService.getCharts(record.payload)
            .pipe(
                map(payload =>
                    chartActions.GetChartsSuccess({payload}),
                    catchError(error => of(chartActions.GetChartsFail({error})))
                )
            )
        )
    ));
}