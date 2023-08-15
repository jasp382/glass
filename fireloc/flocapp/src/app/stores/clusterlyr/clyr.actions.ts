import { createAction, props } from "@ngrx/store";

import { Token } from '../../interfaces/login';
import { ClusterLayer, ClusterLyrAPI, GeoJSONAPI } from "src/app/interfaces/layers";

export const enum clusterLayerTypeAction {
    GET_CLUSTERLYR         = '[GET_CLUSTERLYR] GET CLUSTER LAYERS',
    GET_CLUSTERLYR_SUCCESS = '[GET_CLUSTERLYR_SUCCESS] GET CLUSTER LAYERS SUCCESS',
    GET_CLUSTERLYR_FAIL    = '[GET_CLUSTERLYR_FAIL] GET CLUSTER LAYERS FAIL',

    CLUSTER_WFS         = '[CLUSTER_WFS] GET CLUSTER WFS WITHOUT BOUNDING BOX',
    CLUSTER_WFS_SUCCESS = '[CLUSTER_WFS_SUCCESS] GET CLUSTER WFS WITHOUT BOUNDING BOX SUCCESS',
    CLUSTER_WFS_FAIL    = '[CLUSTER_WFS_FAIL] GET CLUSTER WFS WITHOUT BOUNDING BOX FAIL]',

    CLUSTER_WFSBBOX         = '[CLUSTER_WFSBBOX] GET CLUSTER WFS WITH BOUNDING BOX',
    CLUSTER_WFSBBOX_SUCCESS = '[CLUSTER_WFSBBOX_SUCCESS] GET CLUSTER WFS WITH BOUNDING BOX',
    CLUSTER_WFSBBOX_FAIL    = '[CLUSTER_WFSBBOX_FAIL] GET CLUSTER WFS WITH BOUNDING BOX FAIL',

    ID_CLUSTER         = '[ID_CLUSTER] ID CLUSTER LAYER TO BE IN THE MAP',
    ID_CLUSTER_SUCCESS = '[ID_CLUSTER_SUCCESS] ID CLUSTER LAYER TO BE IN THE MAP SUCCESS',
    ID_CLUSTER_FAIL    = '[ID_CLUSTER_FAIL] ID CLUSTER LAYER TO BE IN THE MAP FAIL',

    SHOW_CLUSTER         = '[SHOW_CLUSTER] CHANGE LAYER SHOW STATUS',
    SHOW_CLUSTER_SUCCESS = '[SHOW_CLUSTER_SUCCESS] CHANGE LAYER SHOW STATUS SUCCESS',
    SHOW_CLUSTER_FAIL    = '[SHOW_CLUSTER_FAIL] CHANGE LAYER SHOW STATUS FAIL'
}

export const GetClusterLayer = createAction(
    clusterLayerTypeAction.GET_CLUSTERLYR,
    props<{ payload: Token }>()
)

export const GetClusterLayerSuccess = createAction(
    clusterLayerTypeAction.GET_CLUSTERLYR_SUCCESS,
    props<{ payload: ClusterLyrAPI }>()
)

export const GetClusterLayerFail = createAction(
    clusterLayerTypeAction.GET_CLUSTERLYR_FAIL,
    props<{ error: string }>()
)

export const ClusterWFS = createAction(
    clusterLayerTypeAction.CLUSTER_WFS,
    props<{ payload: {token: Token, ws: string, lyr: string} }>()
)

export const ClusterWFSSuccess = createAction(
    clusterLayerTypeAction.CLUSTER_WFS_SUCCESS,
    props<{ payload: GeoJSONAPI }>()
)

export const ClusterWFSFail = createAction(
    clusterLayerTypeAction.CLUSTER_WFS_FAIL,
    props<{ error: string }>()
)

export const ClusterWFSBBOX = createAction(
    clusterLayerTypeAction.CLUSTER_WFSBBOX,
    props<{ payload: {token: Token, ws: string, lyr: string, bbox: string} }>()
)

export const ClusterWFSBBOXSuccess = createAction(
    clusterLayerTypeAction.CLUSTER_WFSBBOX_SUCCESS,
    props<{ payload: GeoJSONAPI }>()
)

export const ClusterWFSBBOXFail = createAction(
    clusterLayerTypeAction.CLUSTER_WFSBBOX_FAIL,
    props<{ error: string }>()
)

export const IdCluster = createAction(
    clusterLayerTypeAction.ID_CLUSTER,
    props<{ payload: ClusterLayer }>()
)

export const IdClusterSuccess = createAction(
    clusterLayerTypeAction.ID_CLUSTER_SUCCESS,
    props<{ payload: ClusterLayer }>()
)

export const IdClusterFail = createAction(
    clusterLayerTypeAction.ID_CLUSTER_FAIL,
    props<{ error: string }>()
)

export const ShowStatus = createAction(
    clusterLayerTypeAction.SHOW_CLUSTER,
    props<{ payload: boolean }>()
)

export const ShowStatusSuccess = createAction(
    clusterLayerTypeAction.SHOW_CLUSTER_SUCCESS,
    props<{ payload: boolean }>()
)

export const ShowStatusFail = createAction(
    clusterLayerTypeAction.SHOW_CLUSTER_FAIL,
    props<{ error: string }>()
)