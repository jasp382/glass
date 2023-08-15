import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";
import { ApiStatus } from "src/app/interfaces/general";

import { Chart } from "src/app/interfaces/graphs";

import * as chartActions from './charts.actions';

export interface ChartState {
    charts : Chart[],
    chart  : Chart|null,
    status : ApiStatus|null,
    error  : string|''
}

export const chartsInitialState: ChartState = {
    charts: [], chart: null, status: null, error: ''
}


const _chartsReducer = createReducer(
    chartsInitialState,
    on(chartActions.GetChartsSuccess, (state, { payload }) =>({
        ...state, fireloc: payload.data,
        stctbs: payload.status, error: ''
    })),
    on(chartActions.GetChartsFail, (state, { error }) => ({
        ...state, error: error
    }))
)

export function chartsReducer(state = chartsInitialState, action: Action) {
    return _chartsReducer(state, action);
}


const chartsFeatState = createFeatureSelector<ChartState>(
    'charts'
)

export const getFireloc = createSelector(
    chartsFeatState,
    (state: ChartState) => state.charts
)

export const getFirelocStatus = createSelector(
    chartsFeatState,
    (state: ChartState) => state.status
)