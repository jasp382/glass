import { Injectable } from '@angular/core';
import * as L from 'leaflet';

import { MapSettings } from 'src/app/interfaces/maps';

/**
 * Service for creating and updating a leaflet map. See {@link LeafmapComponent} for usage example.
 */
@Injectable({
  providedIn: 'root'
})
export class MapsService {

  /**
   * Empty constructor
   */
  constructor() { }

  /**
   * Creates a new leaflet map with given settings.
   * @param mapOptions settings for the new map
   * @returns leflet map creating with given settings
   */
  createMap(mapOptions: MapSettings) {
    var newMap = L.map(mapOptions.domElem, {
      minZoom: mapOptions.minZoom,
      maxZoom: mapOptions.maxZoom,
      zoomControl: mapOptions.zoomCtrl
    });

    if (mapOptions.scale) {
      L.control.scale().addTo(newMap);
    }

    // Set map bounds
    let bounds = L.latLngBounds(
      L.latLng(mapOptions.bounds.bottom, mapOptions.bounds.left),
      L.latLng(mapOptions.bounds.top, mapOptions.bounds.right)
    );

    let fullbounds = L.latLngBounds(
      L.latLng(mapOptions.fullext.bottom, mapOptions.fullext.left),
      L.latLng(mapOptions.fullext.top, mapOptions.fullext.right)
    );

    newMap.fitBounds(bounds);
    newMap.setMaxBounds(fullbounds);

    // Set map zoom
    newMap.options.minZoom = newMap.getBoundsZoom(fullbounds);

    return newMap;
  };

  /**
   * Updates the bounds of a leaflet map.
   * @param mapObj map to update the bounds
   * @param mapOptions map settings with desired bounds
   * @returns updated leflet map
   */
  updateBounds(mapObj: any, mapOptions: MapSettings) {
    // Set map bounds
    let bounds = L.latLngBounds(
      L.latLng(mapOptions.bounds.bottom, mapOptions.bounds.left),
      L.latLng(mapOptions.bounds.top, mapOptions.bounds.right)
    );

    let fullbounds = L.latLngBounds(
      L.latLng(mapOptions.fullext.bottom, mapOptions.fullext.left),
      L.latLng(mapOptions.fullext.top, mapOptions.fullext.right)
    );
    mapObj.setMaxBounds(fullbounds);
    mapObj.options.minZoom = mapObj.getBoundsZoom(fullbounds);
    mapObj.fitBounds(bounds);

    return mapObj;
  }
}
