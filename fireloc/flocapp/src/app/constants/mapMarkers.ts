import * as L from 'leaflet';

/**
 * Custom marker for a leaflet map. This marker displays the FireLoc logo.
 */
export const firelocMarker = L.icon({
    iconUrl: '../../assets/images/boff/fireloc-logo.png',
    iconSize: [25, 35],
})