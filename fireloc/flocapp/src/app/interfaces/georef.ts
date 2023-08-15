/* Geo Reference objects */

/**
 * Interface for event 'Freguesia'
 */
export interface Freg {
    /**
     * 'Freguesia' ID
     */
    fid: number,
    /**
     * 'Freguesia' code
     */
    code: string,
    /**
     * 'Freguesia' name
     */
    name: string,
    /**
     * 'Freguesia' 'municícipo' ID
     */
    munid: number
    /**
     * 'Freguesia' geometry
     */
    geom: string|null,
}

/**
 * Interface for Event 'Município'
 */
export interface Mun {
    /**
     * 'Município' ID
     */
    fid: number,
    /**
     * 'Município' code
     */
    code: string,
    /**
     * 'Município' name
     */
    name: string,
    geom: string|null,
    /**
     * 'Município' NUTIII (Nomenclatura das Unidades Territoriais level 3)
     */
    nutiii: number,
}

export interface Place {
    fid: number,
    lugid: string,
    lugname: string,
    altname: string,
    geom: string,
    freg: number,
    source: string,
}