// Generic interfaces

/**
 * @ignore unused interface
 */
export interface ApiStatus {
    code    : string,
    message : string
}

/**
 * @ignore unused interface
 */
export interface Token {
    access_token  : string,
    expires_in    : number,
    token_type    : string,
    scope         : string,
    refresh_token : string,
    role          : string,
    status        : ApiStatus
}