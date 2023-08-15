import { createAction, props } from "@ngrx/store";

import { Token } from '../../interfaces/login';
import { ContribApi, ContribByDayApi, ContribPhoto } from '../../interfaces/contribs';


export const enum ctbTypeAction {
    GET_CONTRIBS         = '[GET_CONTRIBS] GET ALL CONTRIBUTIONS',
    GET_CONTRIBS_SUCCESS = '[GET_CONTRIBS_SUCCESS] GET ALL CONTRIBUTIONS SUCCESS',
    GET_CONTRIBS_FAIL    = '[GET_CONTRIBS_FAIL] GET ALL CONTRIBUTIONS FAIL',

    GET_USER_CONTRIBS         = '[GET_USER_CONTRIBS] GET USER CONTRIBUTIONS',
    GET_USER_CONTRIBS_SUCCESS = '[GET_USER_CONTRIBS_SUCCESS] GET USER CONTRIBUTIONS SUCCESS',
    GET_USER_CONTRIBS_FAIL    = '[GET_USER_CONTRIBS_FAIL] GET USER CONTRIBUTIONS FAIL',

    GET_GEO_CONTRIBS         = '[GET_GEO_CONTRIBS] GET GEO FILTER CONTRIBUTIONS',
    GET_GEO_CONTRIBS_SUCCESS = '[GET_GEO_CONTRIBS_SUCCESS] GET GEO FILTER CONTRIBUTIONS SUCCESS',
    GET_GEO_CONTRIBS_FAIL    = '[GET_GEO_CONTRIBS_FAIL] GET GEO FILTER CONTRIBUTIONS FAIL',

    GET_CONTRIBS_TABLE         = '[GET_CONTRIBS_TABLE] GET CONTRIBUTIONS TABLE',
    GET_CONTRIBS_TABLE_SUCCESS = '[GET_CONTRIBS_TABLE_SUCCESS] GET CONTRIBUTIONS TABLE SUCCESS',
    GET_CONTRIBS_TABLE_FAIL    = '[GET_CONTRIBS_TABLE_FAIL] GET CONTRIBUTIONS TABLE FAIL',

    GET_CONTRIB_PHOTO = '[GET_CONTRIB_PHOTO] GET CONTRIBUTION PHOTO',
    GET_CONTRIB_PHOTO_SUCCESS = '[GET_CONTRIB_PHOTO_SUCCESS] GET CONTRIBUTION PHOTO SUCCESS',
    GET_CONTRIB_PHOTO_FAIL = '[GET_CONTRIB_PHOTO_FAIL] GET CONTRIBUTION PHOTO FAIL',

}

export const GetContribs = createAction(
    ctbTypeAction.GET_CONTRIBS,
    props<{ payload: Token }>()
)

export const GetContribsSuccess = createAction(
    ctbTypeAction.GET_CONTRIBS_SUCCESS,
    props<{ payload: ContribByDayApi }>()
)

export const GetContribsFail = createAction(
    ctbTypeAction.GET_CONTRIBS_FAIL,
    props<{ error: string }>()
)


export const GetUserContribs = createAction(
    ctbTypeAction.GET_USER_CONTRIBS,
    props<{ payload: {token: Token|null, userid: string} }>()
)

export const GetUserContribsSuccess = createAction(
    ctbTypeAction.GET_USER_CONTRIBS_SUCCESS,
    props<{ payload: ContribApi }>()
)

export const GetUserContribsFail = createAction(
    ctbTypeAction.GET_USER_CONTRIBS_FAIL,
    props<{ error: string }>()
)

export const GetGeoContribs = createAction(
    ctbTypeAction.GET_GEO_CONTRIBS,
    props<{ payload: {token: Token|null, fgeom:string} }>()
)

export const GetGeoContribsSuccess = createAction(
    ctbTypeAction.GET_GEO_CONTRIBS_SUCCESS,
    props<{ payload: ContribApi }>()
)

export const GetGeoContribsFail = createAction(
    ctbTypeAction.GET_GEO_CONTRIBS_FAIL,
    props<{ error: string }>()
)


export const GetContribsTable = createAction(
    ctbTypeAction.GET_CONTRIBS_TABLE,
    props<{ payload: { token: Token, strips: number|undefined } }>()
)

export const GetContribsTableSuccess = createAction(
    ctbTypeAction.GET_CONTRIBS_TABLE_SUCCESS,
    props<{ payload: ContribApi }>()
)

export const GetContribsTableFail = createAction(
    ctbTypeAction.GET_CONTRIBS_TABLE_FAIL,
    props<{ error: string }>()
)

export const GetContribPhoto = createAction(
    ctbTypeAction.GET_CONTRIB_PHOTO,
    props<{ payload: {token: Token, photo: string} }>()
)

export const GetContribPhotoSuccess = createAction(
    ctbTypeAction.GET_CONTRIB_PHOTO_SUCCESS,
    props<{ payload: ContribPhoto }>()
)

export const GetContribPhotoFail = createAction(
    ctbTypeAction.GET_CONTRIB_PHOTO_FAIL,
    props<{ error: string }>()
)