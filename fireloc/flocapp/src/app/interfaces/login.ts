import { ApiStatus } from "./general";


export interface Login {
    userid: string,
    password: string
}

export interface Token {
    access_token : string,
    expires_in : number,
    token_type: string,
    scope: string,
    refresh_token: string,
    role: string,
    status: ApiStatus
}


export interface LoginOut {
    token  : Token,
    userid : string
}