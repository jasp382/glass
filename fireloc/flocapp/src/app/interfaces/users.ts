import { ApiStatus } from "./general"
import { FirelocLayer } from "./layers"


/**
 * Interface for a FireLoc user information
 */

export interface UserToken {
    fid: number,
    user_id: number,
    token: string,
    confirmation: boolean
}

export interface User {
    id: number,
    username: string,
    email: string,
    first_name: string,
    last_name: string,
    token: UserToken[],
    usgroup: Group,
    attr : UserAttr[],
    active: boolean,
    status?: ApiStatus
}

export interface UserApi {
    data: User[],
    status: ApiStatus
}


export interface NewUser {
    name: string,
    lastName: string,
    email: string,
    password: string
}


export interface UserProfile {
    /**
     * user ID
     */
    id?: number,
    /**
     * user username
     */
    username?: string,
    /**
     * user email
     */
    email: string,
    /**
     * user first name
     */
    firstName: string,
    /**
     * user surnames
     */
    lastName: string,
    /**
     * @ignore unused
     */
    token?: UserToken[] | null,
    /**
     * user group
     */
    group?: Group | null,
    /**
     * user group name
     */
    groupName?: string,
    /**
     * list of user attribute values
     */
    attr?: UserAttrValue[] | null,
    /**
     * flag for user active state
     */
    active?: boolean,
    /**
     * user password
     */
    password?: string,
}

export interface UserModel {
    id         : number,
    username   : string,
    email      : string,
    first_name : string,
    last_name  : string,
    token      : UserToken[] | null,
    usgroup    : Group[] | null,
    attr       : UserAttrValue[] | null,
    active     : boolean
}


/**
 * Interface for a FireLoc user attribute 
 */
export interface UserAttr {
    /**
     * user attribute ID
     */
    id: number,
    /**
     * user attribute slug
     */
    slug: string,
    /**
     * user attribute name
     */
    name: string,
    /**
     * user attribute type
     */
    type: string
}

/**
 * Interface for a FireLoc user attribute value
 */
export interface UserAttrValue {
    /**
     * attribute value ID
     */
    id?: number,
    /**
     * attribute ID
     */
    attrID: number,
    /**
     * user ID
     */
    user?: number,
    /**
     * attribute value
     */
    value: string,
    /**
     * attribute name
     */
    name: string
}

/**
 * Interface for a FireLoc user group
 */
export interface Group {
    /**
     * group ID
     */
    id: number,
    /**
     * group name
     */
    name: string,
    /**
     * optional list of users
     */
    users: UserProfile[] | null,
    /**
     * optional list of geospatial layers
     */
    layers: FirelocLayer[] | null,

    /**
     * optional flag used for frontend selection of a group
     */
    //selected?: boolean
}

/**
 * @ignore unused interface
 */
export interface Organization {
    id: number,
    alias: string,
    name: string,
    address: string,
    city: string,
    state: string,
    postal: string,
    country: string,
    countryi: string,
    phone: number,
    email: string
}