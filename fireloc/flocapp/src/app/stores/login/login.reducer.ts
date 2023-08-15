import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";

import { Token } from '../../interfaces/login';
import { User } from '../../interfaces/users';

import * as fromLoginAction from './login.actions';


export interface LoginState {
    token: Token | null,
    isLoggedIn: boolean,
    userid: string|null,
    user: User|null,
    recordUser: string|''
    error: string | ''
}

export const loginInitialState: LoginState = {
    token: null,
    isLoggedIn: false,
    userid: null,
    user: null,
    recordUser: '',
    error: ''
}


const _loginReducer = createReducer(
    loginInitialState,
    on(fromLoginAction.LoginUserSuccess, (state, { payload }) => ({
        ...state, token: payload, isLoggedIn: true, error: '',
        userid: null
    })),
    on(fromLoginAction.LoginUserFail, (state, { error }) => ({
        ...state, error: error
    })),
    on(fromLoginAction.UpdateTokenSuccess, (state, { payload }) => ({
        ...state, token: payload, isLoggedIn: true, error: '',
        userid: null
    })),
    on(fromLoginAction.UpdateTokenFail, (state, { error }) => ({
        ...state, error: error
    })),
    on(fromLoginAction.UpdateUserIDSuccess, (state, { payload }) => ({
        ...state, userid: payload
    })),
    on(fromLoginAction.UpdateUserIDFail, (state, { error }) => ({
        ...state, error: error
    })),
    on(fromLoginAction.LogoutUserSuccess, (state, { }) => ({
        ...state, token: null, isLoggedIn: false, error: '',
        userid: null
    })),
    on(fromLoginAction.LogoutUserFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(fromLoginAction.RegisterUserSuccess, (state, { payload }) => ({
        ...state, token: null, isLoggedIn: false, error: '',
        userid: null, recordUser: payload.username
    })),
    on(fromLoginAction.RegisterUserFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(fromLoginAction.LoggedUserSuccess, (state, { payload }) => ({
        ...state, user: payload
    })),
    on(fromLoginAction.LoggedUserFail, (state, { error }) => ({
        ...state, error: error
    }))
);

export function loginReducer(state = loginInitialState, action: Action) {
    return _loginReducer(state, action);
}


const getLoginFeatureState = createFeatureSelector<LoginState>(
    'login'
)

export const getLoginToken = createSelector(
    getLoginFeatureState,
    (state: LoginState) => state.token
)

export const getLoginStatus = createSelector(
    getLoginFeatureState,
    (state: LoginState) => state.isLoggedIn
)

export const getUserID = createSelector(
    getLoginFeatureState,
    (state: LoginState) => state.userid
)

export const getFullState = createSelector(
    getLoginFeatureState,
    (state: LoginState) => state
)

export const getRecordUser = createSelector(
    getLoginFeatureState,
    (state: LoginState) => state.recordUser
)

export const getLogUser = createSelector(
    getLoginFeatureState,
    (state: LoginState) => state.user
)

export const getTokenUserID = createSelector(
    getLoginFeatureState,
    (state: LoginState) => {
        return {token: state.token, userid: state.userid}
    }
)