import { createAction, props } from "@ngrx/store";

import { Token } from '../../interfaces/login';
import { FireEventApi } from "src/app/interfaces/events";


export const enum fireEventsTypeAction {
    GET_FIRE_EVENTS         = '[GET_FIRE_EVENTS] GET FIRE EVENTS',
    GET_FIRE_EVENTS_SUCCESS = '[GET_FIRE_EVENTS_SUCCESS] GET FIRE EVENTS SUCCESS',
    GET_FIRE_EVENTS_FAIL    = '[GET_FIRE_EVENTS_FAIL] GET FIRE EVENTS FAIL'
}


export const GetFireEvents = createAction(
    fireEventsTypeAction.GET_FIRE_EVENTS,
    props<{ payload: Token|null }>()
)

export const GetFireEventsSuccess = createAction(
    fireEventsTypeAction.GET_FIRE_EVENTS_SUCCESS,
    props<{ payload: FireEventApi }>()
)

export const GetFireEventsFail = createAction(
    fireEventsTypeAction.GET_FIRE_EVENTS_FAIL,
    props<{ error: string }>()
)