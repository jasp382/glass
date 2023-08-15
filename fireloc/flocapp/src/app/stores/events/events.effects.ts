import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";

import { EventsService } from "src/app/serv/rest/events.service";

import * as eventsActions from './events.actions';


@Injectable()
export class FireEventsEffects{
    constructor(
        private actions$: Actions,
        private eventsService: EventsService
    ) { }

    getFireEvents$ = createEffect(()=> this.actions$.pipe(
        ofType(eventsActions.fireEventsTypeAction.GET_FIRE_EVENTS),
        exhaustMap((record: any) => this.eventsService.getFireEvents(record.payload, null, null)
            .pipe(
                map(payload =>
                    eventsActions.GetFireEventsSuccess({payload}),
                    catchError(error => of(eventsActions.GetFireEventsFail({error})))
                )
            )
        )
    ));
}