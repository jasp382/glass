/**
 * Interface for Real event. Used in the Geoportal.
 */
export interface RealEvent {
    /**
     * real event start time
     */
    startTime: RealEventDate,
    /**
     * real event end time
     */
    endTime: RealEventDate,
    /**
     * real event cause
     */
    cause: string,
    /**
     * real event name
     */
    name: string,
    /**
     * real event location
     */
    place: string,
    /**
     * real event type
     */
    type: string | null,
    /**
     * real event NCCO code
     */
    codncco: string,
    /**
     * real event SGIF code
     */
    codsgif: string,
}

/**
 * Interface for Real event date values
 */
export interface RealEventDate {
    /**
     * real event year 
     */
    year: string | number,
    /**
     * real event month
     */
    month: string | number,
    /**
     * real event day
     */
    day: string | number,
    /**
     * real event hours
     */
    hour: string | number,
    /**
     * real event minutes
     */
    minute: string | number,
}