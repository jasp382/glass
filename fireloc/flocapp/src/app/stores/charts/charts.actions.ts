import { createAction, props } from "@ngrx/store";

import { Token } from '../../interfaces/login';
import { ChartApi } from "src/app/interfaces/graphs";


export const enum chartTypeAction {
    GET_CHARTS         = '[GET_CHARTS] GET FIRELOC CHARTS',
    GET_CHARTS_SUCCESS = '[GET_CHARTS_SUCCESS] GET FIRELOC CHARTS SUCCESS',
    GET_CHARTS_FAIL    = '[GET_CHARTS_FAIL] GET FIRELOC CHART FAIL'
}


export const GetCharts = createAction(
    chartTypeAction.GET_CHARTS,
    props<{ payload: Token|null }>()
)

export const GetChartsSuccess = createAction(
    chartTypeAction.GET_CHARTS_SUCCESS,
    props<{ payload: ChartApi }>()
)

export const GetChartsFail = createAction(
    chartTypeAction.GET_CHARTS_FAIL,
    props<{ error: string }>()
)