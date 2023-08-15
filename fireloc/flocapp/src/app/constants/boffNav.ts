import { BackofficeLink } from "../interfaces/backoffice";

/**
 * Backoffice Navigation links for side bar navigation.
 */
export class SidebarConstants {

    /**
     * Links for user related components (Users and Groups)
     */
    public static usersLinks: BackofficeLink[] = [{
        link: 'Users', route: 'users', active: false, url: '/admin/users'
    }, {
        link: 'Groups', route: 'groups', active: false, url: '/admin/groups'
    }];

    /**
     * Links for contribution related components (Contributions and Events)
     */
    public static contribLinks: BackofficeLink[] = [{
        link: 'User Contributions', route: 'contribs', active: false, url: '/admin/contribs'
    }, {
        link: 'Events', route: 'events', active: false, url: '/admin/events'
    }];

    /**
     * Links for map related components (Layers, Legend, and Graphs)
     */
    public static mapLinks: BackofficeLink[] = [{
        link: 'Layers', route: 'layers', active: false, url: '/admin/layers'
    }, {
        link: 'Legend', route: 'legend', active: false, url: '/admin/legend'
    }, {
        link: 'Graphs', route: 'graphs', active: false, url: '/admin/graphs'
    }];

    /**
     * Links for geographical datasets related components (Satellite, Raster, and Vetorial)
     */
    public static geosLinks: BackofficeLink[] = [{
        link: 'Satellite Data', route: 'satellite', active: false, url: '/admin/geo/satellite'
    }, {
        link: 'Raster Datasets', route: 'raster', active: false, url: '/admin/geo/raster'
    }, {
        link: 'Vetorial Datasets', route: 'vetorial', active: false, url: '/admin/geo/vetorial'
    }];

    /**
     * Links for other components (Real Events)
     */
    public static otherLinks: BackofficeLink[] = [{
        link: 'Real Events', route: 'real-events', active: false, url: '/admin/real-events'
    }];

}