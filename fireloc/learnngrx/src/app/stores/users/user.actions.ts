import { createAction, props } from "@ngrx/store";
import { UserModel } from "src/app/models/UsersModel";


export const enum usersTypeAction {
    LOAD_USERS = '[LOAD_USERS] LOAD USERS',
    LOAD_USERS_SUCCESS = '[LOAD_USERS_SUCCESS] LOAD USERS SUCCESS',
    LOAD_USERS_FAIL = '[LOAD_USERS_FAIL] LOAD USERS FAIL',

    LOAD_USER = '[LOAD_USER] LOAD USER',
    LOAD_USER_SUCCESS = '[LOAD_USER_SUCCESS] LOAD USER SUCCESS',
    LOAD_USER_FAIL = '[LOAD_USER_FAIL] LOAD USER FAIL',

    ADD_USER = '[ADD_USER] ADD USER',
    ADD_USER_SUCCESS = '[ADD_USER_SUCCESS] ADD USER SUCCESS',
    ADD_USER_FAIL = '[ADD_USER_FAIL] ADD USER FAIL',

    UPDATE_USER = '[UPDATE_USER] UPDATE USER',
    UPDATE_USER_SUCCESS = '[UPDATE_USER_SUCCESS] UPDATE USER SUCCESS',
    UPDATE_USER_FAIL = '[UPDATE_USER_FAIL] UPDATE USER FAIL',

    DEL_USER = '[DEL_USER] DEL USER',
    DEL_USER_SUCCESS = '[DEL_USER_SUCCESS] DEL USER SUCCESS',
    DEL_USER_FAIL = '[DEL_USER_FAIL] DEL USER FAIL',
}

export const LoadUsers = createAction(
    usersTypeAction.LOAD_USERS  
);

export const LoadUsersSuccess = createAction(
    usersTypeAction.LOAD_USERS_SUCCESS,
    props<{ payload: UserModel[] }>()
);

export const LoadUsersFail = createAction(
    usersTypeAction.LOAD_USERS_FAIL,
    props<{ error:string }>()  
);


export const LoadUser = createAction(
    usersTypeAction.LOAD_USER,
    props<{ payload: number }>()  
);

export const LoadUserSuccess = createAction(
    usersTypeAction.LOAD_USER_SUCCESS,
    props<{ payload: UserModel }>()
);

export const LoadUserFail = createAction(
    usersTypeAction.LOAD_USER_FAIL,
    props<{ error:string }>()  
);

export const AddUser = createAction(
    usersTypeAction.ADD_USER,
    props<{ payload: UserModel }>()  
);

export const AddUserSuccess = createAction(
    usersTypeAction.ADD_USER_SUCCESS,
    props<{ payload: UserModel }>()
);

export const AddUserFail = createAction(
    usersTypeAction.ADD_USER_FAIL,
    props<{ error:string }>()  
);

export const UpdateUser = createAction(
    usersTypeAction.UPDATE_USER,
    props<{ payload: UserModel }>()  
);

export const UpdateUserSuccess = createAction(
    usersTypeAction.UPDATE_USER_SUCCESS,
    props<{ payload: UserModel }>()
);

export const UpdateUserFail = createAction(
    usersTypeAction.UPDATE_USER_FAIL,
    props<{ error:string }>()  
);

export const DeleteUser = createAction(
    usersTypeAction.DEL_USER,
    props<{ payload: number }>()  
);

export const DeleteUserSuccess = createAction(
    usersTypeAction.DEL_USER_SUCCESS,
    props<{ payload: number }>()
);

export const DeleteUserFail = createAction(
    usersTypeAction.UPDATE_USER_FAIL,
    props<{ error:string }>()  
);