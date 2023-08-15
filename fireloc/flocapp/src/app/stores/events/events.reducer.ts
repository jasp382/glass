import { Action, createFeatureSelector, createReducer, createSelector, on } from "@ngrx/store";
import { ApiStatus } from "src/app/interfaces/general";

import { FireEvent } from "src/app/interfaces/events";

import * as fireEventsActions from './events.actions';


export interface FireEventsState {
    events : FireEvent[],
    status : ApiStatus|null,
    error  : string | ''
}

export const fireEventsInitialState: FireEventsState = {
    events: [], status: null, error: ''
}



const _fireEventsReducer = createReducer(
    fireEventsInitialState,
    on(fireEventsActions.GetFireEventsSuccess, (state, { payload }) =>({
        ...state, events: payload.data,
        stctbs: payload.status, error: ''
    })),
    on(fireEventsActions.GetFireEventsFail, (state, { error }) => ({
        ...state, error: error
    }))
)

export function fireEventsReducer(state = fireEventsInitialState, action: Action) {
    return _fireEventsReducer(state, action);
}


const fireEventsFeatState = createFeatureSelector<FireEventsState>(
    'fireevents'
)

export const getFireEvents = createSelector(
    fireEventsFeatState,
    (state: FireEventsState) => state.events
)

export const getFireEventsStatus = createSelector(
    fireEventsFeatState,
    (state: FireEventsState) => state.status
)