import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";

import { AuthService } from "src/app/serv/rest/users/auth.service";
import { UserService } from "src/app/serv/rest/users/user.service";

import * as fromLoginAction from './login.actions';


@Injectable()
export class LoginEffects{
    constructor(
        private actions$: Actions,
        private authService: AuthService,
        private userServ: UserService
    ) { }


    goLogin$ = createEffect(()=> this.actions$.pipe(
        ofType(fromLoginAction.loginTypeAction.LOGIN),
        exhaustMap((record: any) => this.authService.login(
            record.payload.userid, record.payload.password)
            .pipe(
                map(payload =>
                    fromLoginAction.LoginUserSuccess({payload}),
                    catchError(error => of(fromLoginAction.LoginUserFail({error})))
                )
            )
        )
    ));

    updateToken$ = createEffect(() => this.actions$.pipe(
        ofType(fromLoginAction.loginTypeAction.UPDATE_TOKEN),
        exhaustMap((record: any) => this.authService.updateToken(record.payload)
            .pipe(
                map(payload =>
                    fromLoginAction.UpdateTokenSuccess({payload}),
                    catchError(error => of(fromLoginAction.UpdateTokenFail({error})))
                )
            )
        )
    ));

    updateUserID$ = createEffect(() => this.actions$.pipe(
        ofType(fromLoginAction.loginTypeAction.UPDATE_USERID),
        exhaustMap((record: any) => this.authService.updateUserID(record.payload)
            .pipe(
                map(payload =>
                    fromLoginAction.UpdateUserIDSuccess({payload}),
                    catchError(error => of(fromLoginAction.UpdateUserIDFail({error})))
                )
            )
        )
    ));

    goLogout$ = createEffect(()=> this.actions$.pipe(
        ofType(fromLoginAction.loginTypeAction.LOGOUT),
        exhaustMap(() => this.authService.logout()
            .pipe(
                map(payload =>
                    fromLoginAction.LogoutUserSuccess(),
                    catchError(error => of(fromLoginAction.LogoutUserFail({error})))
                )
            )
        )
    ));

    recordUser$ = createEffect(()=> this.actions$.pipe(
        ofType(fromLoginAction.loginTypeAction.REGISTER),
        exhaustMap((record:any) => this.authService.registerUser(record.payload)
            .pipe(
                map(payload =>
                    fromLoginAction.RegisterUserSuccess({payload}),
                    catchError(error => of(fromLoginAction.RegisterUserFail({error})))
                )
            )
        )
    ));

    logUser$ = createEffect(()=> this.actions$.pipe(
        ofType(fromLoginAction.loginTypeAction.AUTH_USER),
        exhaustMap((record:any) => this.userServ.getUser(
            record.payload.token, record.payload.userid)
            .pipe(
                map(payload =>
                    fromLoginAction.LoggedUserSuccess({payload}),
                    catchError(error => of(fromLoginAction.LoggedUserFail({error})))
                )
            )
        )
    ));
}