/**
 * Interface for a Backoffice navigation link.
 */
export interface BackofficeLink {
    /**
     * link name
     */
    link: string;
    /**
     * end of the route for frontend detection
     */
    route: string,
    /**
     * flag for frontend detection of active backoffice section
     */
    active: boolean,
    /**
     * internal navigation url used by the router
     */
    url: string
}

/**
 * Interface for a Backoffice table header.
 */
export interface TableHeader {
    /**
     * label to display in table header column
     */
    columnLabel: string,
    /**
     * object property to obtain the values for the table rows
     */
    objProperty: string,
}