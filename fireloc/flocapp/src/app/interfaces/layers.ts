import { ApiStatus } from './general';
import { Group, Organization } from './users';


export interface GeoJSONGeom {
    type: string,
    coordinates: number[]
}

export interface GeoJSONFeat {
    type: string,
    id: string,
    geometry: string,
    geometry_name: string,
    properties: {[key:string] : number|string},
    bbox: number[]
}

export interface GeoJSON {
    type: string,
    features: GeoJSONFeat[],
    totalFeatures: number,
    numberMatched: number,
    timeStamp: string,
    crs: {type: string, properties: {name: string}},
    bbox: number[]
}

export interface GeoJSONAPI {
    status: ApiStatus,
    layer: string,
    data: GeoJSON
}

/**
 * Interface for geospatial layer. Used for Backoffice
 */
export interface FirelocLayer {
    /**
     * layer ID
     */
    id: number,
    /**
     * layer fire ID
     */
    fireID?: number,
    /**
     * layer level
     */
    level?: number,
    /**
     * layer designation
     */
    designation: string,
    /**
     * layer name used in the Geo server
     */
    serverLayer: string,
    /**
     * layer slug
     */
    slug: string,
    /**
     * layer store
     */
    store: string,
    /**
     * layer style
     */
    style: string,
    /**
     * layer workspace
     */
    workspace: string,
    /**
     * layer 'parent' ID
     */
    rootID?: number,
    /**
     * list of layer 'children'
     */
    child?: FirelocLayer[] | null;

    // frontend
    /**
     * flag to frontend layer selection
     */
    selected?: boolean,
    /**
     * flag to identify if a layer is open in the frontend
     */
    isOpen?: boolean,
    /**
     * flag to identify if a layer can be opened in the frontend
     */
    canOpen?: boolean,
}

/**
 * Interface for fireloc layer. Used in geoportal
 */

export interface ViewFirelocLayer {
    id: number,
    slug: string,
    work: string,
    design: string,
    store: string,
    glyr: string,
    style: string,
    flocid: number,
    datehour: string
}

export interface ViewContributionGroup {
    fid : number,
    location: string,
    layers: ViewContributionLayer[]
}

export interface ViewContributionLayer {
    slug: string,
    name: string,
    work: string,
    layer: string,
    style: string|null,
    wms: boolean,
    active: boolean,
    inMap: boolean
}

// Added data from GitHub
/**
 * @ignore unused
 */
export interface LayerLeg {
    id: number,
    minval: string | null,
    maxval: string | null,
    color: string,
    label: string,
    order: number,
    layerid: number
}
// End of added data from GitHub

/**
 * Interface for geospatial layer. Used for Geoportal
 */
export interface Layer {
    /**
     * layer ID
     */
    id: number,
    /**
     * layer level
     */
    level: number,
    /**
     * layer name
     */
    title: string,
    /**
     * layer name used in the Geo Server
     */
    serverLayer: string | null,
    /**
     * layer slug
     */
    slug: string | null;
    /**
     * layer store
     */
    store: string | null;
    /**
     * layer style
     */
    style: string | null;
    /**
     * layer workspace
     */
    workspace: string | null;
    /**
     * list of layer 'children'
     */
    child: Layer[] | null;

    // frontend display
    /**
     * flag to identify if a layer is open in the frontend
     */
    isOpen: boolean;
    /**
     * flag to identify if a layer can be opened in the frontend
     */
    canOpen?: boolean;
}

/**
 * Interface for geospatial layer's Tree
 */

export interface TreeLayerAttr {
    slug    : string,
    label   : string,
    layerid : number
}

export interface TreeLayer {
    id          : number,
    slug        : string,
    designation : string,
    workspace   : string|null,
    store       : string|null,
    gsrvlyr     : string|null,
    style       : string|null,
    rootid      : number,
    level       : number,
    lyrattr     : TreeLayerAttr[],
    child       : TreeLayer[]|null
}

export interface TreeLayerApi {
    data   : TreeLayer[],
    status : ApiStatus
}

/**
 * Interface for real fire events layers
 */

export interface FireEventLayer {
    id: number,
    slug: string,
    design: string,
    work: string,
    store: string,
    glyr: string,
    style: string|null,
    fireid: number
}


export interface ClusterLayer {
    id: number,
    slug: string,
    designation: string,
    workspace: string,
    store: string,
    gsrvlyr: string,
    usgroup: Group[],
    eps: number,
    minzoom: number,
    maxzoom: number,
    minpts: number,
    level: number,
    geojson: GeoJSON|null;
    leaflyr: boolean
}

export interface ClusterLyrAPI {
    data: ClusterLayer[],
    status: ApiStatus
}

export interface SingleCtbLayer {
    id: number,
    slug: string,
    desig: string,
    work: string,
    store: string,
    layer: string,
    style: string|null,
    wms: boolean,
    ctb: number
}


export interface FirelocClusterLayer {
    id: number,
    slug: string,
    designation: string,
    workspace: string,
    store: string,
    gsrvlyr: string,
    usgroup: Group[],
    eps: number,
    minzoom: number,
    maxzoom: number,
    minpts: number,
    level: number,
    geojson: GeoJSON|null;
    leaflyr: boolean
}

export interface FirelocClusterLyrAPI {
    data: FirelocClusterLayer[],
    status: ApiStatus
}