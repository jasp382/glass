import { createAction, props } from "@ngrx/store";

import { User, UserApi } from 'src/app/interfaces/users';
import { Token } from "src/app/interfaces/general";

export const enum userTypeAction {
    GET_USERS         = '[GET_USERS] RETRIEVE ALL USERS',
    GET_USERS_SUCCESS = '[GET_USERS_SUCCESS] RETRIEVE ALL USERS SUCCESS',
    GET_USERS_FAIL    = '[GET_USERS_FAIL] RETRIEVE ALL USERS FAIL',

    GET_USER         = '[GET_USER] GET USER',
    GET_USER_SUCCESS = '[GET_USER_SUCCESS] GET USER SUCCESS',
    GET_USER_FAIL    = '[GET_USER_FAIL] GET USER FAIL',

    ADD_USER = '[ADD_USER] ADD USER',
    ADD_USER_SUCCESS = '[ADD_USER] ADD USER SUCCESS',
    ADD_USER_FAIL = '[ADD_USER] ADD USER SUCCES',

    UPDATE_USER = '[UPDATE_USER] UPDATE USER',
    UPDATE_USER_SUCCESS = '[UPDATE_USER_SUCCESS] UPDATE USER SUCCESS',
    UPDATE_USER_FAIL = '[UPDATE_USER_FAIL] UPDATE USER FAIL',

    DEL_USER = '[DEL_USER] DELETE USER',
    DEL_USER_SUCCESS = '[DEL_USER_SUCCESS] DELETE USER SUCCESS',
    DEL_USER_FAIL = '[DEL_USER_FAIL] DELETE USER FAIL'
}

export const GetUsers = createAction(
    userTypeAction.GET_USERS,
    props<{ payload: Token }>()
);

export const GetUsersSuccess = createAction(
    userTypeAction.GET_USERS_SUCCESS,
    props<{ payload: UserApi }>()
);

export const GetUsersFail = createAction(
    userTypeAction.GET_USERS_FAIL,
    props<{ error: string }>()
);


export const GetUser = createAction(
    userTypeAction.GET_USER,
    props<{ payload: {token: Token, userid: string} }>()
);

export const GetUserSuccess = createAction(
    userTypeAction.GET_USER_SUCCESS,
    props<{ payload: User }>()
);

export const GetUserFail = createAction(
    userTypeAction.GET_USER_FAIL,
    props<{ error: string }>()
);