import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

import * as L from 'leaflet';

import { Basemap } from '../../interfaces/maps';

@Injectable({
  providedIn: 'root'
})
export class BasemapsService {

  /**
   * Empty constructor
   */
  constructor() { }

  getBasemapString(bmap:string): Observable<string> {
    return of(bmap);
  };

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
      
      case "Mapbox Streets":
        return L.tileLayer(
          'https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiamFzcDEyIiwiYSI6ImNqNnRwYnF3MDA0YXkycXM0M210M3FtejQifQ.KfkaOt8Xc02oPI9lBUtHrA',
          { maxZoom: 19, attribution: 'Basemap from @ <a href="https://www.mapbox.com/">Mapbox</a>', tileSize: 512, zoomOffset: -1 }
        );

      case "ESRI Satellite":
        return L.tileLayer('http://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
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
