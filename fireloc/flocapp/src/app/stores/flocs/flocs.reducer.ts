import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";
import { ApiStatus } from "src/app/interfaces/general";

import { Fireloc } from "src/app/interfaces/fireloc";


import * as firelocActions from './flocs.actions';

export interface FirelocState {
    fireloc : Fireloc[],
    status  : ApiStatus|null,
    allflocs : Fireloc[],
    allstatus  : ApiStatus|null,
    error   : string | ''
}

export const firelocInitialState: FirelocState = {
    fireloc: [], status: null, error: '',
    allflocs: [], allstatus: null
}


const _firelocReducer = createReducer(
    firelocInitialState,
    on(firelocActions.GetFirelocSuccess, (state, { payload }) =>({
        ...state, fireloc: payload.data,
        status: payload.status, error: ''
    })),
    on(firelocActions.GetFirelocFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(firelocActions.GetAllFirelocSuccess, (state, { payload }) =>({
        ...state, allflocs: payload.data,
        allstatus: payload.status, error: ''
    })),
    on(firelocActions.GetAllFirelocFail, (state, { error }) => ({
        ...state, error: error
    }))
)

export function firelocReducer(state = firelocInitialState, action: Action) {
    return _firelocReducer(state, action);
}


const firelocFeatState = createFeatureSelector<FirelocState>(
    'fireloc'
)

export const getFireloc = createSelector(
    firelocFeatState,
    (state: FirelocState) => state.fireloc
)

export const getFirelocStatus = createSelector(
    firelocFeatState,
    (state: FirelocState) => state.status
)

export const getAllFireloc = createSelector(
    firelocFeatState,
    (state: FirelocState) => state.allflocs
)