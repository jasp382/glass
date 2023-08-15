import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";

import * as userActions from './users.actions';

import { User } from "src/app/interfaces/users";

export interface UsersState {
    users: User[],
    user: User|null,
    error: string|''
}

export const usersInitialState: UsersState = {
    users: [],
    user: null,
    error: ''
}


const _userReducer = createReducer(
    usersInitialState,
    on(userActions.GetUsersSuccess, (state, { payload }) => ({
        ...state, users: payload.data, error: '',
        cuser: null
    })),
    on(userActions.GetUsersFail, (state, { error }) => ({
        ...state, error: error
    })),

    on(userActions.GetUserSuccess, (state, { payload }) => ({
        ...state, cuser: payload, error: ''
    })),
    on(userActions.GetUserFail, (state, { error }) => ({
        ...state, error: error
    })),
)

export function userReducer(state = usersInitialState, action: Action) {
    return _userReducer(state, action);
}

const getUsersState = createFeatureSelector<UsersState>(
    'users'
)

export const getUsers = createSelector(
    getUsersState,
    (state: UsersState) => state.users
)

export const getCurrentUser = createSelector(
    getUsersState,
    (state: UsersState) => state.user
)