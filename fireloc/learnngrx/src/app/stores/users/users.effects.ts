import { Injectable } from "@angular/core";
import { Actions, createEffect, ofType } from "@ngrx/effects";
import { catchError, exhaustMap, map, of } from "rxjs";
import { UserService } from "src/app/repository/UserService";
import * as fromUsersAction from './user.actions';


@Injectable()
export class UsersEffects{
    constructor(private actions$: Actions, private userService: UserService) {

    }

    loadUsers$ = createEffect(
        ()=> 
            this.actions$.pipe(
                ofType(fromUsersAction.usersTypeAction.LOAD_USERS),
                exhaustMap(() => this.userService.getUsers()
                    .pipe(
                        map(payload => 
                            fromUsersAction.LoadUsersSuccess({payload}),
                            catchError(error => of(fromUsersAction.LoadUsersFail({error})))
                        )
                    )
                )
            )
    )

    loadUser$ = createEffect(
        ()=> 
            this.actions$.pipe(
                ofType(fromUsersAction.usersTypeAction.LOAD_USER),
                exhaustMap((record: any) => this.userService.getUser(record.payload)
                    .pipe(
                        map(payload => 
                            fromUsersAction.LoadUserSuccess({payload}),
                            catchError(error => of(fromUsersAction.LoadUserFail({error})))
                        )
                    )
                )
            )
    )

    addUser$ = createEffect(
        ()=> 
            this.actions$.pipe(
                ofType(fromUsersAction.usersTypeAction.ADD_USER),
                exhaustMap((record: any) => this.userService.addUser(record.payload)
                    .pipe(
                        map(payload => 
                            fromUsersAction.AddUserSuccess({payload}),
                            catchError(error => of(fromUsersAction.AddUserFail({error})))
                        )
                    )
                )
            )
    )

    updateUser$ = createEffect(
        ()=> 
            this.actions$.pipe(
                ofType(fromUsersAction.usersTypeAction.UPDATE_USER),
                exhaustMap((record: any) => this.userService.updateUser(record.payload)
                    .pipe(
                        map(payload => 
                            fromUsersAction.UpdateUserSuccess({payload}),
                            catchError(error => of(fromUsersAction.UpdateUserFail({error})))
                        )
                    )
                )
            )
    )

    delUser$ = createEffect(
        ()=> 
            this.actions$.pipe(
                ofType(fromUsersAction.usersTypeAction.DEL_USER),
                exhaustMap((record: any) => this.userService.delUser(record.payload)
                    .pipe(
                        map(() => 
                            fromUsersAction.DeleteUserSuccess({payload: record.payload}),
                            catchError(error => of(fromUsersAction.DeleteUserFail({error})))
                        )
                    )
                )
            )
    )
}