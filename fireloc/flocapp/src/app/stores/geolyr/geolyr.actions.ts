import { createAction, props } from "@ngrx/store";

import { Token } from '../../interfaces/login';
import { TreeLayerApi } from '../../interfaces/layers';


export const enum treeLayerTypeAction {
    GET_TREELAYERS         = '[GET_TREELAYERS] GET TREE LAYERS',
    GET_TREELAYERS_SUCCESS = '[GET_TREELAYERS_SUCCESS] GET TREE LAYERS SUCCESS',
    GET_TREELAYERS_FAIL    = '[GET_TREELAYERS_FAIL] GET TREE LAYERS FAIL'
}

export const GetTreeLayer = createAction(
    treeLayerTypeAction.GET_TREELAYERS,
    props<{ payload: { token: Token|null, astree: boolean } }>()
)

export const GetTreeLayerSuccess = createAction(
    treeLayerTypeAction.GET_TREELAYERS_SUCCESS,
    props<{ payload: TreeLayerApi }>()
)

export const GetTreeLayerFail = createAction(
    treeLayerTypeAction.GET_TREELAYERS_FAIL,
    props<{ error: string }>()
)