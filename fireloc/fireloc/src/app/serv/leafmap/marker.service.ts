import { Injectable } from '@angular/core';
import * as L from 'leaflet';

/**
 * Service for adding markers to a leaflet map.
 */
@Injectable({
  providedIn: 'root'
})
export class MarkerService {

  /**
   * Empty constructor
   */
  constructor() { }

  /**
   * Adds default leafleat marker to map at desired coordinates.
   * @param map leaflet map to add the marker to
   * @param lat latitude of the desired marker location
   * @param long longitude of the desired marker location
   */
  addMarkerToMap(map: L.Map, lat: number, long: number) { L.marker([lat, long]).addTo(map); }

  /**
   * Adds custom leafleat marker to map at desired coordinates.
   * @param map leaflet map to add the marker to
   * @param lat latitude of the desired marker location
   * @param long longitude of the desired marker location
   * @param markerIcon custom icon to be added to the map
   */
  addCustomMarkerToMap(map: L.Map, lat: number, long: number, markerIcon: any) {
    L.marker([lat, long], { icon: markerIcon }).addTo(map);
  }

  /**
   * Creates a new feature group and adds it to a leaflet map.
   * See [Backoffice Real Events]{@link RealEventsComponent#createPolyline} for usage example.
   * @param map leaflet map to add the feature group to
   * @returns feature group reference already added to the map
   */
  startPolylineGroup(map: L.Map): L.FeatureGroup { return L.featureGroup().addTo(map); }

  /**
   * Adds a new line to a feature group after clearing said feature group.
   * See [Backoffice Real Events]{@link RealEventsComponent#createPolyline} for usage example.
   * @param pointList list of points with coordinates to create the new line
   * @param polygroup feature group to add the line to
   */
  addPolylineToFilterMap(pointList: any[], polygroup: L.FeatureGroup) {
    this.clearPolyGroup(polygroup);
    var line = L.polyline(pointList, { color: 'red' }).addTo(polygroup);
    line.addLatLng(pointList[0]);
  }

  /**
   * Adds a new closed polygon to a feature group after clearing said feature group.
   * See [Backoffice Real Events]{@link RealEventsComponent#createPolyline} for usage example.
   * @param pointList list of points with coordinates to create the new polygon
   * @param polygroup feature group to add the polygon to
   */
  addPolygonToFilterMap(pointList: any[], polygroup: L.FeatureGroup) {
    this.clearPolyGroup(polygroup);
    L.polygon(pointList, { color: 'red' }).addTo(polygroup);
  }

  /**
   * Clears all layers of a map feature group.
   * @param polygroup feature group to be cleared
   */
  clearPolyGroup(polygroup: L.FeatureGroup) { polygroup.clearLayers(); }


  /**
   * Adds a new line to a feature group.
   * @param pointList list of points with coordinates to create the new line
   * @param polygroup feature group to add the line to
   */
  addPolylineToMap(pointList: any[], polygroup: L.FeatureGroup) {
    var line = L.polyline(pointList, { color: 'red' }).addTo(polygroup);
    line.addLatLng(pointList[0]);
  }

  /**
   * Adds a new closed polygon to a feature group.
   * @param pointList list of points with coordinates to create the new polygon
   * @param polygroup feature group to add the polygon to
   */
  addPolygonToMap(pointList: any[], polygroup: L.FeatureGroup) { L.polygon(pointList, { color: 'red' }).addTo(polygroup); }

  // --- Contribution Layers

  /**
   * Adds a GeoJSON layer to a marker cluster group. 
   * See [Geoportal Main Component]{@link MainfrontComponent#getContribLayer} for usage example.
   * @param geoJsonData GeoJSON data to add to the marker cluster group
   * @param clusterGroup marker cluster group to add the layer to
   */
  addGeoLayerToCluster(geoJsonData: any, clusterGroup: L.MarkerClusterGroup) {
    let geoJsonLayer = L.geoJSON(geoJsonData);
    clusterGroup.addLayer(geoJsonLayer);
  }
}
