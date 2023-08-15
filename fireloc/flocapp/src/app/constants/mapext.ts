import { Bounds } from "../interfaces/maps";

/**
 * Constants for the Leaflet maps
 */
export class Extent {
    /**
     * Bounds for the map
     */
    public static bounds: Bounds = {
        left   : -9.50052660716585,
        right  : -6.189159307482962,
        bottom : 36.9617104661766,
        top    : 42.15431112740946,
    };

    /**
     * Maximum bounds for the map
     */
    public static maxBounds: Bounds = {
        left   : -9.50052660716585,
        right  : -6.189159307482962,
        bottom : 36.9617104661766,
        top    : 42.15431112740946,
    };
}