/* Interfaces related with maps */

import { Group, Organization } from "./users";

/**
 * Interface for map bounds
 */
export interface Bounds {
    /**
     * bottom bound
     */
    bottom: number,
    /**
     * top bound
     */
    top: number,
    /**
     * left bound
     */
    left: number,
    /**
     * right bound
     */
    right: number
}

/**
 * Interface for leaflet map base layer
 */
export interface Basemap {
    [key: string]: any
}

/**
 * Interface for map web service layers
 */
export interface MapLayer {
    /**
     * layer ID
     */
    id: number,
    /**
     * layer slug
     */
    slug: string,
    /**
     * layer level
     */
    level: number,
    /**
     * layer designation
     */
    designation: string,
    /**
     * layer workspace
     */
    workspace: string,
    /**
     * layer store
     */
    store: string,
    /**
     * layer name used for Geo Server
     */
    serverLayer: string,
    /**
     * layer style
     */
    style?: string,
    /**
     * layer minimum zoom (related to map zoom value)
     */
    minZoom: number,
    /**
     * layer maximum zoom (related to map zoom value)
     */
    maxZoom: number,
    /* usgroup: Group[] | null,
    orgs: Organization[] | null */
}

/**
 * Interface for leaflet map settings
 */
export interface MapSettings {
    /**
     * HTML element ID where map is placed
     */
    domElem: string,
    /**
     * HTML element class for map container
     */
    mapContainer: string,
    /**
     * map minimum zoom value
     */
    minZoom: number,
    /**
     * map maximum zoom value
     */
    maxZoom: number,
    /**
     * map scale
     */
    scale: boolean,
    /**
     * flag for map to contain zoom controls to increase or decrease zoom
     */
    zoomCtrl: boolean,
    /**
     * map bounds
     */
    bounds: Bounds,
    /**
     * maximum map bounds
     */
    fullext: Bounds,
    /**
     * @ignore unused
     */
    wfs: MapLayer[],
    /**
     * @ignore unused
     */
    wms: MapLayer[]
}