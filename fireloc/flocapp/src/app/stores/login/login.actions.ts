import { createAction, props } from "@ngrx/store";

import { Login, Token } from "src/app/interfaces/login";
import { NewUser, User } from "src/app/interfaces/users";

export const enum loginTypeAction {
    LOGIN         = '[LOGIN] USER LOGIN',
    LOGIN_SUCCESS = '[LOGIN_SUCCESS] USER LOGIN SUCCESS',
    LOGIN_FAIL    = '[LOGIN_FAIL] USER LOGIN FAIL',

    UPDATE_TOKEN = '[UPDATE_TOKEN] UPDATE TOKEN FROM LOCAL STORAGE',
    UPDATE_TOKEN_SUCCESS = '[UPDATE_TOKEN] UPDATE TOKEN SUCCESS',
    UPDATE_TOKEN_FAIL = '[UPDATE_TOKEN] UPDATE TOKEN FAIL',

    UPDATE_USERID         = '[UPDATE_USERID] UPDATE USER ID',
    UPDATE_USERID_SUCCESS = '[UPDATE_USERID_SUCCESS] UPDATE USER ID SUCCESS',
    UPDATE_USERID_FAIL    = '[UPDATE_USERID_FAIL] UPDATE USER ID FAIL',

    LOGOUT         = '[LOGOUT] USER LOGOUT',
    LOGOUT_SUCCESS = '[LOGOUT_SUCCESS] USER LOGOUT SUCCESS',
    LOGOUT_FAIL    = '[LOGOUT_FAIL] USER LOGOUT SUCCESS',

    REGISTER         = '[REGISTER] REGISTER NEW USER',
    REGISTER_SUCCESS = '[REGISTER] REGISTER NEW USER SUCCESS',
    REGISTER_FAIL    = '[REGISTER] REGISTER NEW USER FAIL',

    AUTH_USER = '[AUTH_USER] RETRIEVE AUTHENTICATED USER',
    AUTH_USER_SUCCESS = '[AUTH_USER_SUCCESS] RETRIEVE AUTHENTICATED USER SUCCESS',
    AUTH_USER_FAIL = '[AUTH_USER_FAIL] RETRIEVE AUTHENTICATED USER FAIL'
}

export const LoginUser = createAction(
    loginTypeAction.LOGIN,
    props<{ payload: Login }>()
);

export const LoginUserSuccess = createAction(
    loginTypeAction.LOGIN_SUCCESS,
    props<{ payload: Token }>()
)

export const LoginUserFail = createAction(
    loginTypeAction.LOGIN_FAIL,
    props<{ error: string }>()
)

export const UpdateToken = createAction(
    loginTypeAction.UPDATE_TOKEN,
    props<{ payload: Token }>()
);

export const UpdateTokenSuccess = createAction(
    loginTypeAction.UPDATE_TOKEN_SUCCESS,
    props<{ payload: Token }>()
)

export const UpdateTokenFail = createAction(
    loginTypeAction.UPDATE_TOKEN_FAIL,
    props<{ error: string }>()
)

export const UpdateUserID = createAction(
    loginTypeAction.UPDATE_USERID,
    props<{ payload: string }>()
);

export const UpdateUserIDSuccess = createAction(
    loginTypeAction.UPDATE_USERID_SUCCESS,
    props<{ payload: string }>()
)

export const UpdateUserIDFail = createAction(
    loginTypeAction.UPDATE_USERID_FAIL,
    props<{ error: string }>()
)

export const LogoutUser = createAction(
    loginTypeAction.LOGOUT
);

export const LogoutUserSuccess = createAction(
    loginTypeAction.LOGOUT_SUCCESS
)

export const LogoutUserFail = createAction(
    loginTypeAction.LOGOUT_FAIL,
    props<{ error: string }>()
)

export const RegisterUser = createAction(
    loginTypeAction.REGISTER,
    props<{ payload: NewUser }>()
);

export const RegisterUserSuccess = createAction(
    loginTypeAction.REGISTER_SUCCESS,
    props<{ payload: User }>()
)

export const RegisterUserFail = createAction(
    loginTypeAction.REGISTER_FAIL,
    props<{ error: string }>()
)


export const LoggedUser = createAction(
    loginTypeAction.AUTH_USER,
    props<{ payload: {token: Token, userid: string} }>()
);

export const LoggedUserSuccess = createAction(
    loginTypeAction.AUTH_USER_SUCCESS,
    props<{ payload: User }>()
)

export const LoggedUserFail = createAction(
    loginTypeAction.AUTH_USER_FAIL,
    props<{ error: string }>()
)