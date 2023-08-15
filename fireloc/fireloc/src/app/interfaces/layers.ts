import { Group, Organization } from './users';

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