import { Freg, Mun } from "./georef";
import { FirelocLayer } from "./layers";

/**
 * Interface for Real event. Used for Backoffice
 */
export interface RealEvent {
    /**
     * real event ID
     */
    id: number,
    /**
     * real event name
     */
    name: string | null,
    /**
     * real event type
     */
    type: string | null,
    /**
     * real event start time
     */
    startTime: string,
    /**
     * real event end time
     */
    endTime: string,
    /**
     * real event geospatial geometry
     */
    geom: string | null,
    /**
     * real event cause
     */
    cause: string | null,
    /**
     * real event SGIF code (Sistema de Gestão de Informação de Incêndios Florestais)
     */
    codSGIF: string | null,
    /**
     * real event NCCO code
     */
    codNCCO: string | null,
    /**
     * real event burned area in hectares
     */
    burnedArea: number,
    /**
     * list of real event layers
     */
    fireLayers: FirelocLayer[] | null,
    /**
     * real event 'Freguesia'
     */
    freg: Freg | null,
    /**
     * real event 'Município'
     */
    mun: Mun | null,
}

/**
 * Interface for a FireLoc event
 */
export interface Event {
    /**
     * event ID
     */
    id: number,
    /**
     * event start date
     */
    startTime: EventDate,
    /**
     * event end date
     */
    endTime: EventDate | null,
    /**
     * event contributions start date
     */
    contribStart: EventDate,
    /**
     * event contributions end date
     */
    contribEnd: EventDate,
    /**
     * close place ID
     */
    nearPlace: number,
    /**
     * event 'Município'
     */
    mun?: string,
    /**
     * event 'Freguesia'
     */
    freg?: string,
    /**
     * @ignore unused
     */
    ncbt?: number,
    /**
     * list of contribution photo names
     */
    contributionPhotos: string[],
    /**
     * list of event service layers
     */
    layers: ServiceLayer[],
    /**
     * event place location
     */
    place: EventPlace,
    /**
     * list of event attributes
     */
    attributes: EventAttribute[],
}

/**
 * Interface for a FireLoc event date values
 */
export interface EventDate {
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

/**
 * Interface for a FireLoc event service layer
 */
export interface ServiceLayer {
    /**
     * layer ID
     */
    id: number,
    /**
     * GeoServer layer name
     */
    gLayer: string,
    /**
     * layer slug
     */
    slug: string,
    /**
     * Layer store
     */
    store: string,
    /**
     * Layer style
     */
    style: string,
    /**
     * Layer workspace
     */
    work: string,
    /**
     * Layer designation
     */
    design: string,
}

/**
 * Interface for a FireLoc event location
 */
export interface EventPlace {
    /**
     * place ID
     */
    id: number,
    /**
     * 'Freguesia' ID
     */
    fregID: number,
    /**
     * 'Lugar' ID
     */
    lugID: number,
    /**
     * geospatial place geometry
     */
    geom: string,
    /**
     * place source
     */
    source?: string,
    /**
     * place name
     */
    name: string,
    /**
     * place alternative name
     */
    altName?: string,
}

/**
 * Interface for a FireLoc event attribute
 */
export interface EventAttribute {
    /**
     * attribute ID
     */
    id: number,
    /**
     * attribute slug
     */
    slug: string,
    /**
     * attribute name
     */
    name: string,
    /**
     * attribute name
     */
    value: string,
}