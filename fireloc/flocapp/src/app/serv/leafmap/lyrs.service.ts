import { Injectable } from '@angular/core';

// Leaflet
import * as L from 'leaflet';

import { BasemapsService } from './basemaps.service';

import { Observable, of } from 'rxjs';
import { MappingLayer } from 'src/app/interfaces/maps';
import { SingleCtbLayer, ViewContributionGroup, ViewContributionLayer, ViewFirelocLayer } from 'src/app/interfaces/layers';
import { Contrib } from "src/app/interfaces/contribs";

import { api } from 'src/app/apicons';


/**
 * Service for leaflet map layers management.
 */
@Injectable({
  providedIn: 'root'
})
export class LyrsService {

  /**
   * Empty constructor
   */
  constructor(
    private bmaps: BasemapsService
  ) { }

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

  isFireloc(o:any): o is ViewFirelocLayer {
    return true;
  }


  addNewMapLayer(layer: ViewFirelocLayer): Observable<MappingLayer> {
    let mapLayer: MappingLayer = {
      slug: layer.slug,
      displayName: layer.design,
      workspace: layer.work,
      serverLayer: layer.glyr,
      style: layer.style,
      active: true
    };

    return of(mapLayer);
  };

  addNewContribLayer(lyr: Contrib): Observable<ViewContributionGroup> {
    let layers: ViewContributionLayer[] = [];
    
    if (lyr.layers?.length) {
      for (let _l of lyr.layers) {
        let _lyr: ViewContributionLayer = {
          slug: _l.slug,
          name: _l.desig,
          work: _l.work,
          layer: _l.layer,
          style: _l.style,
          wms: _l.wms,
          active: true,
          inMap: false
        };

        layers.push(_lyr);
      }
    }

    let mapLayer: ViewContributionGroup = {
      fid: lyr.fid,
      location: lyr.place !== null ? lyr.place.lugname : lyr.fregid.name,
      layers: layers
    };

    return of(mapLayer);
  }

  wmsLayer(ws: string, lyr: string, style: string) {
    return L.tileLayer.wms(api.wmsUrl + ws + '/', {
      layers: lyr,
      format: 'image/png',
      transparent: true,
      styles: style
    })
  }
}
