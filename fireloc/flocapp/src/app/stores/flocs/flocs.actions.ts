import { createAction, props } from "@ngrx/store";

import { Token } from '../../interfaces/login';
import { FirelocApi } from "src/app/interfaces/fireloc";


export const enum firelocTypeAction {
    GET_FIRELOC         = '[GET_FIRELOC] GET FIRELOC OBSERVATIONS',
    GET_FIRELOC_SUCCESS = '[GET_FIRELOC_SUCCESS] GET FIRELOC OBSERVATIONS SUCCESS',
    GET_FIRELOC_FAIL    = '[GET_FIRELOC_FAIL] GET FIRELOC OBSERVATIONS FAIL',

    ALL_FIRELOC         = '[ALL_FIRELOC] GET ALL FIRELOC OBSERVATIONS',
    ALL_FIRELOC_SUCCESS = '[ALL_FIRELOC_SUCCESS] GET ALL FIRELOC OBSERVATIONS SUCCESS',
    ALL_FIRELOC_FAIL    = '[ALL_FIRELOC_FAIL] GET ALL FIRELOC OBSERVATIONS FAIL'
}


export const GetFireloc = createAction(
    firelocTypeAction.GET_FIRELOC,
    props<{ payload: {token: Token|null, step: string } }>()
)

export const GetFirelocSuccess = createAction(
    firelocTypeAction.GET_FIRELOC_SUCCESS,
    props<{ payload: FirelocApi }>()
)

export const GetFirelocFail = createAction(
    firelocTypeAction.GET_FIRELOC_FAIL,
    props<{ error: string }>()
)

export const GetAllFireloc = createAction(
    firelocTypeAction.ALL_FIRELOC,
    props<{ payload: Token }>()
)

export const GetAllFirelocSuccess = createAction(
    firelocTypeAction.ALL_FIRELOC_SUCCESS,
    props<{ payload: FirelocApi }>()
)

export const GetAllFirelocFail = createAction(
    firelocTypeAction.ALL_FIRELOC_FAIL,
    props<{ error: string }>()
)