import * as L from 'leaflet';

import { Basemap } from '../interfaces/maps';

/**
 * Class for getting a base layer for a leaflet map.
 * 
 * See {@link MapsService} for service using it.
 */
export class Basemaps {
  /**
   * List of services available for getting a base layer
   */
  public static servicesList: string[] = ["OpenStreetMap", "ESRI Streets", "Satellite"];

  /**
   * Get base layer for leaflet map according to chosen service.
   * @param {string} service Name of the service to request the layer from 
   * @returns Tile Layer ready for addition to a leaflet map
   */
  public getLayer(service: string): Basemap {
    switch (service) {
      case "OpenStreetMap":
        return L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        });

      case "ESRI Streets":
        return L.tileLayer('http://services.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
          maxZoom: 19, attribution: '&copy; @ESRI'
        });
      case "Satellite":
        return L.tileLayer(
          'https://api.mapbox.com/v4/{id}/{z}/{x}/{y}@2x.jpg90?access_token=pk.eyJ1IjoiamFzcDEyIiwiYSI6ImNqNnRwYnF3MDA0YXkycXM0M210M3FtejQifQ.KfkaOt8Xc02oPI9lBUtHrA',
          { maxZoom: 19, attribution: 'Basemap from @ <a href="https://www.mapbox.com/">Mapbox</a>', tileSize: 512, zoomOffset: -1, id: 'mapbox.satellite' }
        );
      // default is OpenStreetMap
      default:
        return L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        });
    }
  }
}