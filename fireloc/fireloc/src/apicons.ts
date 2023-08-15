/**
 * Class holding all API URLs used to make API calls. See services for usage examples.
 */
export class api {
    /**
     * root URL used for API calls
     */
    /* public static url: string = "https://locusignis.dei.uc.pt/"; */
    public static url: string = "http://127.0.0.1:8000/";
    /* public static url: string = "https://vgi.mat.uc.pt/"; */

    // Authentication
    /**
     * Authentication URL to get a new authentication token
     */
    public static tokenurl: string = api.url + 'auth/token/new/';
    /**
     * Authentication URL to renew an authentication token
     */
    public static renewurl: string = api.url + 'auth/token/renew/';

    // User Management
    /**
     * User URL to perform actions on users
     */
    public static usersUrl: string = api.url + 'auth/users/';
    /**
     * User URL to perform actions on a single user with privileges
     */
    public static userUrl: string = api.url + 'auth/user/'
    /**
     * User URL to perform actions on a single user without privileges
     */
    public static justuserUrl: string = api.url + 'auth/justauser/';
    /**
     * User URL to perform actions on user attributes
     */
    public static attrsUrl: string = api.url + 'auth/attrs/';
    /**
     * User URL to perform actions on a single user attribute
     */
    public static attrUrl: string = api.url + 'auth/attr/';
    /**
     * User URL to request password recovery
     */
    public static recoverpswUrl: string = api.url + 'auth/request-pass-recovery/';
    /**
     * User URL to request password change after recovery request
     */
    public static changepswUrl: string = api.url + 'auth/pass-recovery/';
    /**
     * User URL to request registration confirmation
     */
    public static regconfirmationUrl: string = api.url + 'auth/rqstconfirmation/';

    // Group Management
    /**
     * Group URL to perform actions on user groups
     */
    public static groupsUrl: string = api.url + 'auth/groups/';
    /**
     * Group URL to perform actions on a single user group
     */
    public static groupUrl: string = api.url + 'auth/group/';

    // Contribution Management
    /**
     * Contribution URL to perform actions on user contributions
     */
    public static contribsUrl: string = api.url + 'volu/contributions/';

    // Event Management
    /**
     * Event URL to perform actions on FireLoc events (authentication required)
     */
    public static eventTokenUrl: string = api.url + 'floc/fireloc/';
    /**
     * Event URL to perform actions on FireLoc events (no authentication required)
     */
    public static eventUrl: string = api.url + 'floc/fireloc-uu/';

    // Real Event Management
    /**
     * Real Event URL to perform actions on real events (authentication required)
     */
    public static realEventsTokenUrl: string = api.url + 'events/real-fires/';
    /**
     * Real Event URL to perform actions on a single real event
     */
    public static realEventTokenUrl: string = api.url + 'events/real-fire/';
    /**
     * Real Event URL to perform actions on real events (no authentication required)
     */
    public static realEventsUrl: string = api.url + 'events/rfires-uu/';

    // Layer Management
    /**
     * Layer URL to perform actions on FireLoc layers (authentication required)
     */
    public static layersTokenUrl: string = api.url + 'geovis/geoportal-layers/';
    /**
     * Layer URL to perform actions on a single FireLoc layer
     */
    public static layerUrl: string = api.url + 'geovis/geoportal-layer/';
    /**
     * Layer URL to perform actions on FireLoc layers (no authentication required)
     */
    public static layersUrl: string = api.url + 'geovis/glayers-uu/';
    /**
     * Layer URL to perform actions on FireLoc layers in user groups
     */
    public static groupLayersUrl: string = api.url + 'geovis/layers-groups/';
    /**
     * Layer URL to perform actions on FireLoc layers in contributions
     */
    public static contribLayersUrl: string = api.url + 'geovis/contrib-layers/';

    // Chart Management
    /**
     * Chart URL to perform actions on charts
     */
    public static chartsUrl: string = api.url + 'geovis/geo-charts/';
    /**
     * Chart URL to perform actions on a single chart
     */
    public static chartUrl: string = api.url + 'geovis/geo-chart/';

    // Raster Dataset Management
    /**
     * Raster Dataset URL to perform actions on raster datasets
     */
    public static rasterDatasetsUrl: string = api.url + 'georst/raster-datasets/';
    /**
     * Raster Dataset URL to perform actions on a single raster dataset
     */
    public static rasterDatasetUrl: string = api.url + 'georst/raster-dataset/';
    /**
     * Raster Dataset URL to perform actions on raster dataset types
     */
    public static rasterTypesUrl: string = api.url + 'georst/raster-types/';

    // Satellite Dataset Management
    /**
     * Satellite Dataset URL to perform actions on satellite datasets
     */
    public static satDatasetsUrl: string = api.url + 'geosat/sentinel-imgs/';
    /**
     * Satellite Dataset URL to perform actions on a single satellite dataset
     */
    public static satDatasetUrl: string = api.url + 'geosat/sentinel-img/';

    // Vector Dataset Management
    /**
     * Vector Dataset URL to perform actions on vector datasets
     */
    public static vecDatasetsUrl: string = api.url + 'geovec/vector-datasets/';
    /**
     * Vector Dataset URL to perform actions on a single vector dataset
     */
    public static vecDatasetUrl: string = api.url + 'geovec/vector-dataset/';
    /**
     * Vector Dataset URL to perform actions on vector dataset categories
     */
    public static vecCategoriesUrl: string = api.url + 'geovec/vector-cats/';
    /**
     * Vector Dataset URL to perform actions on vector dataset levels
     */
    public static vecLevelsUrl: string = api.url + 'geovec/vector-levels/';
    /**
     * Vector Dataset URL to perform actions on a single vector dataset level
     */
    public static vecLevelUrl: string = api.url + 'geovec/vector-level/';

    // GeoServer Map Services
    /**
     * GeoServer Map Services URL to perform actions on map services
     */
    public static geoMapServicesUrl: string = api.url + 'geosrv/wfs/';

}