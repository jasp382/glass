import { createAction, props } from "@ngrx/store";
import { Contrib } from "src/app/interfaces/contribs";
import { ViewContributionGroup, ViewFirelocLayer } from "src/app/interfaces/layers";
import { MappingLayer } from "src/app/interfaces/maps";


export const enum leafMapActions {
    UPDATE_BASEMAP = '[UPDATE_BASEMAP] UPDATE BASEMAP',
    UPDATE_BASEMAP_SUCCESS = '[UPDATE_BASEMAP_SUCCESS] UPDATE BASEMAP SUCCESS',
    UPDATE_BASEMAP_FAIL = '[UPDATE_BASEMAP_FAIL] UPDATE BASEMAP FAIL',

    ADD_WMS         = '[ADD_WMS] ADD WMS LAYER',
    ADD_WMS_SUCCESS = '[ADD_WMS_SUCCESS] ADD WMS LAYER SUCCESS',
    ADD_WMS_FAIL    = '[ADD_WMS_FAIL] ADD WMS LAYER FAIL',

    ADD_CTBWMS         = '[ADD_CTBWMS] ADD CONTRIBUTION WMS LAYER',
    ADD_CTBWMS_SUCCESS = '[ADD_CTBWMS_SUCCESS] ADD CONTRIBUTION WMS LAYER SUCCESS',
    ADD_CTBWMS_FAIL    = '[ADD_CTBWMS] ADD CONTRIBUTION WMS LAYER FAIL',
}


export const UpdateBasemap = createAction(
    leafMapActions.UPDATE_BASEMAP,
    props<{ payload: string }>()
)

export const UpdateBasemapSuccess = createAction(
    leafMapActions.UPDATE_BASEMAP_SUCCESS,
    props<{ payload: string }>()
);

export const UpdateBasemapFail = createAction(
    leafMapActions.UPDATE_BASEMAP_FAIL,
    props<{ error: string }>()
)

export const AddWMS = createAction(
    leafMapActions.ADD_WMS,
    props<{ payload: ViewFirelocLayer }>()
)

export const AddWMSSuccess = createAction(
    leafMapActions.ADD_WMS_SUCCESS,
    props<{ payload: MappingLayer }>()
);

export const AddWMSFail = createAction(
    leafMapActions.ADD_WMS_FAIL,
    props<{ error: string }>()
)


export const AddContributionWMS = createAction(
    leafMapActions.ADD_CTBWMS,
    props<{ payload: Contrib }>()
)

export const AddContributionWMSSuccess = createAction(
    leafMapActions.ADD_CTBWMS_SUCCESS,
    props<{ payload: ViewContributionGroup }>()
);

export const AddContributionWMSFail = createAction(
    leafMapActions.ADD_CTBWMS_FAIL,
    props<{ error: string }>()
)