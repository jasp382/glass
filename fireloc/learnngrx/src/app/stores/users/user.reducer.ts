import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";
import { UserModel } from "src/app/models/UsersModel";
import * as fromUsersAction from "../users/user.actions"




export interface UsersState {
    users: UserModel[],
    user: UserModel | null,
    error: string | ''
}

export const initialState: UsersState = {
    users: [],
    user: null,
    error: ''
}


const _usersReducer = createReducer(
    initialState,
    on(fromUsersAction.LoadUsersSuccess, (state, { payload }) => ({...state, users: payload, error: ''})),
    on(fromUsersAction.LoadUsersFail, (state, { error }) => ({...state, error: error})),

    on(fromUsersAction.LoadUserSuccess, (state, { payload }) => ({...state, user: payload, error: ''})),
    on(fromUsersAction.LoadUserFail, (state, { error }) => ({...state, error: error})),

    on(fromUsersAction.AddUserSuccess, (state, { payload }) => ({...state, users: [...state.users, payload], error: ''})),
    on(fromUsersAction.AddUserFail, (state, { error }) => ({...state, error: error})),

    on(fromUsersAction.UpdateUserSuccess, (state, { payload }) => ({
        ...state, 
        users: [...state.users].map((row) => {
            if (row.id == payload.id) {
                return payload;
            } else {
                return row;
            }
        }),
        error: ''})),
    on(fromUsersAction.UpdateUserFail, (state, { error }) => ({...state, error: error})),

    on(fromUsersAction.DeleteUserSuccess, (state, { payload }) => ({
        ...state,
        users: [...state.users].filter((filter) => filter.id != payload),
        error: ''
    })),
    on(fromUsersAction.DeleteUserFail, (state, { error }) => ({...state, error: error})),
);


export function usersReducer(state = initialState, action: Action) {
    return _usersReducer(state, action);
}


const getUsersFeatureState = createFeatureSelector<UsersState>(
    'users'
)

export const getUsers = createSelector(
    getUsersFeatureState,
    (state: UsersState) => state.users
)

export const getUser = createSelector(
    getUsersFeatureState,
    (state: UsersState) => state.user
)

export const getUserError = createSelector(
    getUsersFeatureState,
    (state: UsersState) => state.error
)


export const getUsersAdmin = createSelector(
    getUsersFeatureState,
    (state: UsersState) => state.users.filter((filter) => filter.profile == 'admin')
)

export const getUsersParam = createSelector(
    getUsersFeatureState,
    (state: UsersState, props: {profile: string}) => state.users.filter((filter) => filter.profile == props.profile)
)

export const getUsersAge50 = createSelector(
    getUsersFeatureState,
    (state: UsersState) => state.users.filter((filter) => filter.age >= 50)
)