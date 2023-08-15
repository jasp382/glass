import { Freg, Place } from "./georef";
import { ApiStatus } from "./general";
import { SingleCtbLayer } from "./layers";


export interface Contrib {
    fid: number,
    pic: string,
    respic: string|null,
    datehour: string,
    dateday: string,
    dist: string | null,
    direction: number,
    dsun: number | null,
    directbf: number | null,
    orie: number | null,
    beta: number | null,
    gama: number | null,
    txt: string | null,
    pnt_name: string | null,
    fire_name: string | null,
    ugazimute: number | null,
    gazimute: number | null,
    gbfazimute: number | null,
    strips: number,
    photostatus: number,
    timestamp: number,
    place: Place | null,
    fregid: Freg,
    cuser: number,
    geom: GeomData[],
    geomc: {x_coord: number, y_coord: number},
    geombfc: string | null,
    usergeom: string | null,
    geombf: GeomData[] | null,
    layers: SingleCtbLayer[]|null
}

/**
 * @ignore unused interface
 */
export interface GeomData {
    pid: number,
    azimute: number,
    geom: string
}

export interface ContribApi {
    data: Contrib[],
    status: ApiStatus
}

/**
 * Interface for grouping FireLoc contributions by contribution date
 */
export interface ContribByDay {
    dateday: string,
    ctbs: Contrib[]
}

export interface ContribByDayApi {
    data: ContribByDay[],
    status: ApiStatus
}

export interface ContribAux {
    hour : number|string,
    minute: number|string,
    location: string
}

export interface ContribAuxDay {
    date: ContribDate,
    ctbs: ContribAux[]
}

/**
 * Interface for a FireLoc contribution
 */
export interface Contribution {
    /**
     * contribution ID
     */
    fid: number,
    /**
     * contribution photo name
     */
    pic: string,
    /**
     * contribution location
     */
    location: string,
    /**
     * contribution date
     */
    date: ContribDate,
    /**
     * contribution hours
     */
    hour: string | number,
    /**
     * contribution minutes
     */
    minute: string | number,
    /**
     * contribution geospatial geometry
     */
    geom: Geom[],
    /**
     * contribution direction
     */
    dir: number,
    /**
     * contribution sun direction
     */
    dsun: number | null,
    /**
     * contribution average latitude
     */
    avgLat?: number | string,
    /**
     * contribution average longitude
     */
    avgLong?: number | string
}


export interface ContributionDateGroup {
    /**
     * date of the contributions
     */
    date: ContribDate,
    /**
     * list of contributions with the same date
     */
    contributions: Contribution[]
}

/**
 * Interface for FireLoc contribution date values
 */
export interface ContribDate {
    /**
     * contribution year
     */
    year: string | number,
    /**
     * contribution month
     */
    month: string | number,
    /**
     * contribution day
     */
    day: string | number,
}

/**
 * Interface for FireLoc contribution geospatial geometry values
 */
export interface Geom {
    /**
     * point ID
     */
    pid: number,
    /**
     * point latitude
     */
    lat: number,
    /**
     * point longitude
     */
    long: number
}

export interface ContribPhoto {
    status: ApiStatus,
    data  : string
}