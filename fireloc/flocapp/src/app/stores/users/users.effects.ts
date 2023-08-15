import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";

import { UserService } from "src/app/serv/rest/users/user.service";

import * as userActions from './users.actions';

@Injectable()
export class UserEffects{
    constructor(
        private actions$: Actions,
        private userServ: UserService
    ) { }

    getUsers$ = createEffect(()=> this.actions$.pipe(
        ofType(userActions.userTypeAction.GET_USERS),
        exhaustMap((record: any) => this.userServ.getUsers(record.payload)
            .pipe(
                map(payload =>
                    userActions.GetUsersSuccess({payload}),
                    catchError(error => of(userActions.GetUsersFail({error})))
                )
            )
        )
    ));

    getUser$ = createEffect(()=> this.actions$.pipe(
        ofType(userActions.userTypeAction.GET_USER),
        exhaustMap((record: any) => this.userServ.getUser(
            record.payload.token, record.payload.userid)
            .pipe(
                map(payload =>
                    userActions.GetUserSuccess({payload}),
                    catchError(error => of(userActions.GetUserFail({error})))
                )
            )
        )
    ));
}