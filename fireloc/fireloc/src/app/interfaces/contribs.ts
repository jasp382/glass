import { Freg, Place } from "./georef";

// Added data from GitHub
/**
 * @ignore unused interface
 */
export interface ContributionsList {
    fid: number,
    pic: string | null,
    datehour: string,
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
    fireassess: number | null,
    photoclass: number | null,
    photostatus: number | null,
    ugazimute: number | null,
    gazimute: number | null,
    gbfazimute: number | null,
    timestamp: number,
    place: Place | null,
    fregid: Freg | null,
    cuser: number,
    geom: GeomData[],
    geomc: string,
    geombfc: string | null,
    usergeom: string | null,
    geombf: GeomData[] | null,
    strips: number
}

/**
 * @ignore unused interface
 */
export interface GeomData {
    pid: number,
    azimute: number,
    geom: string
}
// End of added data from GitHub

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

/**
 * Interface for grouping FireLoc contributions by contribution date
 */
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