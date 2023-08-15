/* Geo Reference objects */

/**
 * Interface for event 'Freguesia'
 */
export interface Freg {
    /**
     * 'Freguesia' ID
     */
    id: number,
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
    gem?: string,
}

/**
 * Interface for Event 'Município'
 */
export interface Mun {
    /**
     * 'Município' ID
     */
    id: number,
    /**
     * 'Município' code
     */
    code: string,
    /**
     * 'Município' name
     */
    name: string,
    /**
     * 'Município' NUTIII (Nomenclatura das Unidades Territoriais level 3)
     */
    NUTiii: number,
}

// Added data from GitHub
/**
 * @ignore unused
 */
export interface Place {
    fid: number,
    lugid: string,
    lugname: string,
    altname: string,
    geom: string,
    freg: number,
    source: string,
}
// End of added data from GitHub