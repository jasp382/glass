import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";
import { ApiStatus } from "src/app/interfaces/general";

import { Contrib, ContribByDay } from "src/app/interfaces/contribs";


import * as ctbActions from './ctb.actions';



export interface ContribState {
    ctbs     : ContribByDay[],
    photo    : string|'',
    myctbs   : Contrib[],
    geoctbs  : Contrib[],
    stctbs   : ApiStatus|null,
    stmyctbs : ApiStatus|null,
    stgeoctb : ApiStatus|null,
    ctbstbl  : Contrib[],
    stctbtbl : ApiStatus|null,
    error    : string | ''
}

export const ctbInitialState: ContribState = {
    ctbs: [], photo: '',
    myctbs: [], geoctbs: [],
    stctbs: null, stmyctbs: null, stgeoctb: null,
    ctbstbl: [],
    stctbtbl: null,
    error: ''
}


const _contribReducer = createReducer(
    ctbInitialState,
    on(ctbActions.GetContribsSuccess, (state, { payload }) =>({
        ...state, ctbs: payload.data,
        stctbs: payload.status, error: ''
    })),
    on(ctbActions.GetContribsFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(ctbActions.GetUserContribsSuccess, (state, { payload }) =>({
        ...state, myctbs: payload.data,
        stmyctbs: payload.status, error: ''
    })),
    on(ctbActions.GetUserContribsFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(ctbActions.GetGeoContribsSuccess, (state, { payload }) =>({
        ...state, geoctbs: payload.data,
        stgeoctb: payload.status, error: ''
    })),
    on(ctbActions.GetGeoContribsFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(ctbActions.GetContribsTableSuccess, (state, { payload }) =>({
        ...state, ctbstbl: payload.data,
        stctbtbl: payload.status, error: ''
    })),
    on(ctbActions.GetContribsTableFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(ctbActions.GetContribPhotoSuccess, (state, { payload }) =>({
        ...state, photo: 'data:image/jpg;base64,' + payload.data,
        error: ''
    })),
    on(ctbActions.GetContribPhotoFail, (state, { error }) => ({
        ...state, error: error
    }))
)

export function contribReducer(state = ctbInitialState, action: Action) {
    return _contribReducer(state, action);
}


const contribFeatureState = createFeatureSelector<ContribState>(
    'contrib'
)

export const getAllContrib = createSelector(
    contribFeatureState,
    (state: ContribState) => state.ctbs
)

export const getAllContribStatus = createSelector(
    contribFeatureState,
    (state: ContribState) => state.stctbs
)

export const getUserContrib = createSelector(
    contribFeatureState,
    (state: ContribState) => state.myctbs
)

export const getUserContribStatus = createSelector(
    contribFeatureState,
    (state: ContribState) => state.stmyctbs
)

export const getGeoContrib = createSelector(
    contribFeatureState,
    (state: ContribState) => state.geoctbs
)

export const getGeoContribStatus = createSelector(
    contribFeatureState,
    (state: ContribState) => state.stgeoctb
)


export const getContribPhoto = createSelector(
    contribFeatureState,
    (state: ContribState) => state.photo
)
