// ----- SATELLITE
/**
 * Interface for Satellite dataset. Used in the Backoffice. 
 */
export interface SentinelImg {
    // identifiers
    /**
     * dataset ID
     */
    id: number,
    /**
     * dataset identifier
     */
    identifier: string,
    /**
     * dataset data strip identifier
     */
    dataStripIdentifier: string,
    /**
     * dataset granule identifier
     */
    granuleIdentifier: string,
    /**
     * dataset level 1 CPDI identifier
     */
    level1CpdiIdentifier: string,
    /**
     * dataset platform identifier
     */
    platformIdentifier: string,
    /**
     * dataset platform serial identifer
     */
    platformSerialIdentifier: string | null,
    /**
     * dataset S2 data take ID
     */
    s2DataTakeId: string,
    /**
     * dataset universally unique identifier
     */
    uuid: string,

    /**
     * dataset title
     */
    title: string,
    /**
     * dataset summary 
     */
    summary: string,

    // positions and dates
    /**
     * dataset begin position date
     */
    beginPositionDate: string,
    /**
     * dataset end position date
     */
    endPositionDate: string,
    /**
     * dataset ingestion date
     */
    ingestionDate: string,
    /**
     * dataset generation date
     */
    generationDate: string,

    // percentages
    /**
     * dataset cloud coverage percentage
     */
    cloudCoverPercentage: string,
    /**
     * dataset medium probability of clouds percentage
     */
    mediumProbCloudsPercentage: string,
    /**
     * dataset high probability of clouds percentage
     */
    highProbCloudsPercentage: string,
    /**
     * dataset vegetation percentage
     */
    vegetationPercentage: string,
    /**
     * dataset not vegetated percentage
     */
    notVegetatedPercentage: string,
    /**
     * dataset water percentage
     */
    waterPercentage: string,
    /**
     * dataset unclassified percentage
     */
    unclassifiedPercentage: string,
    /**
     * dataset snow and ice percentage
     */
    snowIcePercentage: string,

    // orbit and geometry
    /**
     * dataset orbit number
     */
    orbitNumber: number,
    /**
     * dataset relative orbit number
     */
    relativeOrbitNumber: number,
    /**
     * dataset orbit direction
     */
    orbitDirection: string,
    /**
     * dataset geometry
     */
    geometry: string,
    /**
     * dataset illumination azimuth angle
     */
    illuminationAzimuthAngle: number | null,
    /**
     * dataset illumination zenith angle
     */
    illuminationZenithAngle: number | null,

    // processing
    /**
     * dataset processing baseline
     */
    processingBaseline: string,
    /**
     * dataset processing level
     */
    processingLevel: string,

    // checks
    /**
     * dataset check for demand
     */
    onDemand: string,
    /**
     * dataset check for downloadable
     */
    isDownload: boolean,

    // other    
    /**
     * dataset file name
     */
    fileName: string,
    /**
     * dataset link
     */
    link: string,
    /**
     * dataset format
     */
    format: string,
    /**
     * dataset platform name
     */
    platformName: string,
    /**
     * dataset instrument name
     */
    instrumentName: string,
    /**
     * dataset instrument name abbreviated
     */
    instrumentShortName: string,
    /**
     * dataset file size
     */
    size: string,
    /**
     * dataset product type
     */
    productType: string,

    /* fireref: number, */
    /* cellid: number, */
    /* isab: boolean */
}

// ----- RASTER

// Added data from GitHub
/**
 * @ignore unused
 */
export interface RasterLayers {
    layer: string,
    cellsizex: number | null,
    cellsizey: number | null,
    method: string,
    level: string,
    refgrid: number,
    idrst: number
}
// End of added data from GitHub

/**
 * Interface for Raster dataset type
 */
export interface RasterType {
    /**
     * type ID
     */
    id: number,
    /**
     * type slug
     */
    slug: string,
    /**
     * type name
     */
    name: string,
    /**
     * type description
     */
    description: string,

    // frontend
    /**
     * flag to identify if type is selected in the frontend
     */
    selected?: boolean,
}

/**
 * Interface for Raster Dataset. Used in the Backoffice.
 */
export interface RasterDataset {
    /**
     * dataset ID
     */
    id: number,
    /**
     * dataset slug
     */
    slug: string,
    /**
     * dataset name
     */
    name: string,
    /**
     * dataset description
     */
    description: string,
    /**
     * dataset year of data
     */
    refYear: number | null,
    /**
     * dataset year of production
     */
    refProd: number | null,
    /**
     * dataset source
     */
    source: string,
    /**
     * dataset type ID
     */
    typeID: number,
    /**
     * dataset type
     */
    type?: RasterType,
    /* layers: RasterLayers[] | null */
}

// ----- VECTORIAL
/**
 * Interface for Vetorial Dataset. Used in the Backoffice.
 */
export interface VectorDataset {
    /**
     * dataset ID
     */
    id: number,
    /**
     * dataset slug
     */
    slug: string,
    /**
     * dataset name
     */
    name: string,
    /**
     * dataset description
     */
    description: string,
    /**
     * dataset source
     */
    source: string,
    /**
     * dataset year of data
     */
    refYear: number | null,
    /**
     * dataset year of production
     */
    refProd: number | null,
    /**
     * dataset geometry type
     */
    geometryType: string,
    /**
     * dataset category ID
     */
    categoryID: number,
    /**
     * dataset category
     */
    category?: VectorCategory,
    /**
     * list of dataset levels
     */
    datasetLevels: VectorLevel[]
}

/**
 * Interface for a Vetorial dataset level
 */
export interface VectorLevel {
    /**
     * level ID
     */
    id: number,
    /**
     * level slug
     */
    slug: string,
    /**
     * level name
     */
    name: string,
    /**
     * level description
     */
    description: string,
    /**
     * level actual level value
     */
    level: number,
}

/**
 * Interface for a Vetorial dataset category
 */
export interface VectorCategory {
    /**
     * category ID
     */
    id: number,
    /**
     * cateogry slug
     */
    slug: string,
    /**
     * category name
     */
    name: string,
    /**
     * category description
     */
    description: string,
    // frontend
    /**
     * flag to identify if category is selected in the frontend
     */
    selected?: boolean,
}