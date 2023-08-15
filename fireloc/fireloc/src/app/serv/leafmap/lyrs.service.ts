import { Injectable } from '@angular/core';
import { Basemap } from 'src/app/interfaces/maps';
import { Basemaps } from 'src/app/util/basemaps';

/**
 * Service for leaflet map layers management.
 */
@Injectable({
  providedIn: 'root'
})
export class LyrsService {

  /**
   * Class with available map base layers
   */
  bmaps: Basemap = new Basemaps();

  /**
   * Empty constructor
   */
  constructor() { }

  /**
   * Updates the base layer of a leaflet map.
   * @param mapObj leaflet map to be updated
   * @param basemap new desired base layer service name
   * @returns updated leaflet map
   */
  updateBasemap(mapObj: any, basemap: string) {
    var layer = this.bmaps.getLayer(basemap);
    mapObj.addLayer(layer);
    return mapObj;
  }

  /**
   * Adds a layer to a leaflet map.
   * @param map leaflet map to add the layer to
   * @param layer layer to be added
   */
  addLayer(map: L.Map, layer: any) { map.addLayer(layer); }

  /**
   * Removes a layer from a leaflet map.
   * @param map leaflet map to remove the layer from
   * @param layer layer to be removed
   */
  removeLayer(map: L.Map, layer: any) { map.removeLayer(layer); }
}
