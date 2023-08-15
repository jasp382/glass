import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";
import { ApiStatus } from "src/app/interfaces/general";

import { ClusterLayer } from "src/app/interfaces/layers";

import * as cLyrActions from './clyr.actions';


export interface ClusterLayerState {
    layers : ClusterLayer[],
    isActive: boolean,
    status : ApiStatus|null,
    error  : string|''
}

export const cLayerInitialState: ClusterLayerState = {
    layers: [], isActive: true, status: null, error: ''
}

const _clusterLayerReducer = createReducer(
    cLayerInitialState,
    on(cLyrActions.GetClusterLayerSuccess, (state, { payload }) => ({
        ...state, layers: payload.data,
        status: payload.status, error: ''
    })),
    on(cLyrActions.GetClusterLayerFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(cLyrActions.ClusterWFSSuccess, (state, { payload }) => ({
        ...state,
        layers: [...state.layers].map((row) => {
            if (row.gsrvlyr === payload.layer) {
                let nlyr: ClusterLayer = {
                    id: row.id,
                    slug: row.slug,
                    designation: row.designation,
                    workspace: row.workspace,
                    store: row.store,
                    gsrvlyr: row.gsrvlyr,
                    usgroup: row.usgroup,
                    eps: row.eps,
                    minzoom: row.minzoom,
                    maxzoom: row.maxzoom,
                    minpts: row.minpts,
                    level: row.level,
                    geojson: payload.data,
                    leaflyr: row.leaflyr
                };

                return nlyr
            } else {
                return row;
            }
        }),
        status: payload.status, error: ''
    })),
    on(cLyrActions.ClusterWFSFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(cLyrActions.ClusterWFSBBOXSuccess, (state, { payload }) => ({
        ...state,
        layers: [...state.layers].map((row) => {
            if (row.gsrvlyr === payload.layer) {
                let nlyr: ClusterLayer = {
                    id: row.id,
                    slug: row.slug,
                    designation: row.designation,
                    workspace: row.workspace,
                    store: row.store,
                    gsrvlyr: row.gsrvlyr,
                    usgroup: row.usgroup,
                    eps: row.eps,
                    minzoom: row.minzoom,
                    maxzoom: row.maxzoom,
                    minpts: row.minpts,
                    level: row.level,
                    geojson: payload.data,
                    leaflyr: row.leaflyr
                };

                return nlyr
            } else {
                return row;
            }
        }),
        status: payload.status, error: ''
    })),
    on(cLyrActions.ClusterWFSBBOXFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(cLyrActions.IdClusterSuccess, (state, { payload }) => ({
        ...state,
        layers: [...state.layers].map((row) => {
            if (row.gsrvlyr === payload.gsrvlyr) {
                let nlyr: ClusterLayer = {
                    id: payload.id,
                    slug: payload.slug,
                    designation: payload.designation,
                    workspace: payload.workspace,
                    store: payload.store,
                    gsrvlyr: payload.gsrvlyr,
                    usgroup: payload.usgroup,
                    eps: payload.eps,
                    minzoom: payload.minzoom,
                    maxzoom: payload.maxzoom,
                    minpts: payload.minpts,
                    level: payload.level,
                    geojson: payload.geojson,
                    leaflyr: true
                };

                return nlyr
            } else {
                let _nlyr: ClusterLayer = {
                    id: row.id,
                    slug: row.slug,
                    designation: row.designation,
                    workspace: row.workspace,
                    store: row.store,
                    gsrvlyr: row.gsrvlyr,
                    usgroup: row.usgroup,
                    eps: row.eps,
                    minzoom: row.minzoom,
                    maxzoom: row.maxzoom,
                    minpts: row.minpts,
                    level: row.level,
                    geojson: row.geojson,
                    leaflyr: false
                };
                return _nlyr;
            }
        }),
        error: ''
    })),
    on(cLyrActions.IdClusterFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(cLyrActions.ShowStatusSuccess, (state, { payload }) => ({
        ...state, isActive : payload, error: ''
    })),
    on(cLyrActions.ShowStatusFail, (state, { error }) => ({
        ...state, error: error
    })),
);

export function clusterLayerReducer(state = cLayerInitialState, action: Action) {
    return _clusterLayerReducer(state, action)
}


const ctbLayerFeatureState = createFeatureSelector<ClusterLayerState>(
    'clusterlayer'
)

export const getCusterLayers = createSelector(
    ctbLayerFeatureState,
    (state: ClusterLayerState) => state.layers
)

export const getCusterLayerStatus = createSelector(
    ctbLayerFeatureState,
    (state: ClusterLayerState) => state.status
)

export const custerIsActive = createSelector(
    ctbLayerFeatureState,
    (state: ClusterLayerState) => state.isActive
)