/* Fire location detection related */

import { ViewFirelocLayer } from "./layers";
import { Contrib } from "./contribs";
import { Place, Freg, Mun } from "./georef";

import { ApiStatus } from './general';


export interface FirelocAttr {
    id: number,
    dtype: string,
    fattr: number,
    floc: 1,
    slug: string,
    name: string,
    value: string,
    pointgeom: string | null,
    polygeom: string | null
}


export interface Fireloc {
    id: number,
    startime: string|null,
    endtime: string|null,
    ctbstart: string,
    ctbend: string,
    aprch: number,
    nearplace: number | null,
    extent: string,
    fregid: number|null,
    step: number,
    place: Place | null,
    freg: Freg,
    prid: string,
    geom: string|null,
    flocctb: Contrib[],
    floclyr: ViewFirelocLayer[],
    attr: FirelocAttr[]|null,
    mun: Mun,
    cctb: number
}
// End of added data from GitHub

export interface FirelocApi {
    data: Fireloc[],
    status: ApiStatus
}

/**
 * Interface for a FireLoc event date values
 */
export interface FirelocDate {
    /**
     * event year
     */
    year: string | number,
    /**
     * event month
     */
    month: string | number,
    /**
     * event day
     */
    day: string | number,
    /**
     * event hours
     */
    hour: string | number,
    /**
     * event minutes
     */
    minute: string | number,
}

export interface FirelocAux {
    startTime: FirelocDate|null,
    endTime : FirelocDate|null,
    contribStart: FirelocDate,
    contribEnd: FirelocDate
}