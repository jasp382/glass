/* Fire location detection related */

import { FirelocLayer } from "./layers";
import { ContributionsList } from "./contribs";
import { Place } from "./georef";

// Added data from GitHub
/**
 * @ignore unused interface
 */
export interface ObsFireAttr {
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

/**
 * @ignore unused interface
 */
export interface ObsFire {
    id: number,
    startime: string,
    endtime: string,
    contribstart: string,
    contribend: string,
    isfire: boolean,
    aprch: number,
    proid: number,
    nearplace: number | null,
    place: Place | null,
    flocctb: ContributionsList[],
    floclyr: FirelocLayer[],
    attr: ObsFireAttr[]
}
// End of added data from GitHub