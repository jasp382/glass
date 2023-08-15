import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";
import { ApiStatus } from "src/app/interfaces/general";

import { TreeLayer } from '../../interfaces/layers';

import * as layerActions from './geolyr.actions';


export interface TreeLayerState {
    layers : TreeLayer[],
    status : ApiStatus|null,
    error  : string | ''
}

export const layerInitialState: TreeLayerState = {
    layers: [], status: null, error: ''
}


const _treeLayerReducer = createReducer(
    layerInitialState,
    on(layerActions.GetTreeLayerSuccess, (state, { payload }) => ({
        ...state, layers: payload.data,
        status: payload.status, error: ''
    })),
    on(layerActions.GetTreeLayerFail, (state, { error }) => ({
        ...state, error: error
    }))
);

export function treeLayerReducer(state = layerInitialState, action: Action) {
    return _treeLayerReducer(state, action)
}


const treeLayerFeatureState = createFeatureSelector<TreeLayerState>(
    'treelayer'
)

export const getTreeLayer = createSelector(
    treeLayerFeatureState,
    (state: TreeLayerState) => state.layers
)

export const getTreeLayerStatus = createSelector(
    treeLayerFeatureState,
    (state: TreeLayerState) => state.status
)