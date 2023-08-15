import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";

import { Fireloc } from "src/app/interfaces/fireloc";


import { MappingLayer, Bounds } from "src/app/interfaces/maps";
import { ViewContributionGroup } from "src/app/interfaces/layers";

import * as leafActions from './leaf.actions';

export interface LeafmapState {
    basemap: string,
    maplayers: MappingLayer[],
    ctblayers: ViewContributionGroup[],
    floclayers: Fireloc[],
    mapBounds: Bounds|null,
    error: string|''
}


export const leafMapInitialState: LeafmapState = {
    basemap: 'OpenStreetMap',
    maplayers: [],
    ctblayers: [], floclayers: [],
    mapBounds: null,
    error  : ''
}

const _leafMapReducer = createReducer(
    leafMapInitialState,
    on(leafActions.UpdateBasemapSuccess, (state, { payload }) =>({
        ...state, basemap: payload, error: ''
    })),
    on(leafActions.UpdateBasemapFail, (state, { error }) => ({
        ...state, error: error
    })),
    on(leafActions.AddWMSSuccess, (state, { payload }) =>({
        ...state, maplayers: [payload, ...state.maplayers], error: ''
    })),
    on(leafActions.AddWMSFail, (state, { error }) => ({
        ...state, error: error
    })),

    // Update contributions layers
    on(leafActions.AddContributionWMSSuccess, (state, { payload }) =>({
        ...state, ctblayers: [payload, ...state.ctblayers], error: ''
    })),
    on(leafActions.AddContributionWMSFail, (state, { error }) => ({
        ...state, error: error
    })),
)


export function leafMapReducer(state = leafMapInitialState, action: Action) {
    return _leafMapReducer(state, action);
}


const leafFeatureState = createFeatureSelector<LeafmapState>(
    'leafmap'
)

export const getBasemap = createSelector(
    leafFeatureState,
    (state: LeafmapState) => state.basemap
)

export const getMapLayers = createSelector(
    leafFeatureState,
    (state: LeafmapState) => state.maplayers
)

export const getContribLayers = createSelector(
    leafFeatureState,
    (state: LeafmapState) => state.ctblayers
)
