import { ActionReducerMap } from "@ngrx/store";
import { usersReducer, UsersState } from "./users/user.reducer";
import { UsersEffects } from "./users/users.effects";


export interface AppState {
    users: UsersState
}

export const appReducer: ActionReducerMap<AppState> = {
    users: usersReducer
}

export const appEffects = [
    UsersEffects
]