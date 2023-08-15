import { Injectable } from '@angular/core';

import * as L from 'leaflet';

const bigSkyIcon = L.icon({
  iconUrl: '../../assets/icons/blue-big.png',
  iconSize: [50, 50],
  iconAnchor: [25, 50],
  tooltipAnchor: [0, -50],
  popupAnchor: [0, -50]
});

const bigRedIcon = L.icon({
  iconUrl: '../../assets/icons/red-big.png',
  iconSize: [50, 50],
  iconAnchor: [25, 50],
  tooltipAnchor: [0, -50],
  popupAnchor: [0, -50]
});

const bigGreenIcon = L.icon({
  iconUrl: '../../assets/icons/green-big.png',
  iconSize: [50, 50],
  iconAnchor: [25, 50],
  tooltipAnchor: [0, -50],
  popupAnchor: [0, -50]
});

const skyIcon = L.icon({
  iconUrl: '../../assets/icons/map-pin-sky.png',
  iconSize: [25, 25],
  iconAnchor: [12.5, 25],
  tooltipAnchor: [0, -50],
  popupAnchor: [0, -50]
});

const optimalIcon = L.icon({
  iconUrl: '../../assets/icons/map-pin-optimal.png',
  iconSize: [25, 25],
  iconAnchor: [12.5, 25],
  tooltipAnchor: [0, -50],
  popupAnchor: [0, -50]
});

const warningIcon = L.icon({
  iconUrl: '../../assets/icons/map-pin-warning.png',
  iconSize: [25, 25],
  iconAnchor: [12.5, 25],
  tooltipAnchor: [0, -50],
  popupAnchor: [0, -50]
});

const dangerIcon = L.icon({
  iconUrl: '../../assets/icons/map-pin-danger.png',
  iconSize: [25, 25],
  iconAnchor: [12.5, 25],
  tooltipAnchor: [0, -50],
  popupAnchor: [0, -50]
});

/**
 * Service for adding markers to a leaflet map.
 */
@Injectable({
  providedIn: 'root'
})
export class MarkerService {

  activeMarker: any = undefined;

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
  addGeoLayerToCluster(geoJsonData: any): L.MarkerClusterGroup {
    var activeMarker = this.activeMarker;

    var clusterGroup = L.markerClusterGroup({
      iconCreateFunction: function(cluster) {
        var icons = cluster.getAllChildMarkers();
        return L.divIcon({
          className: 'mapCluster',
          html: "<p class='m-0'><b>" + cluster.getChildCount() + '</b></p>'
        });
      },
      polygonOptions: {
        fillColor: '#36B9CC',
        color: '#36B9CC',
        weight: 0.5,
        opacity: 1,
        fillOpacity: 0.5
      }
    });

    let geoJsonLayer = L.geoJSON(geoJsonData, {
      pointToLayer: function (feature, latLng) {
        var icon = feature.properties.icon;
        var activeIcon = icon === 'sky' ? skyIcon : dangerIcon;

        var _lyr = L.marker(latLng, {icon: activeIcon}).on({
          mouseover: icon === 'sky' ? setBlueBigIcon : setRedBigIcon,
          mouseout : icon === 'sky' ? setBlueIcon : setRedIcon,
          click : icon === 'sky' ? clickedBlueIcon: clickedRedIcon,
          popupclose: icon === 'sky' ? closeBluePopup: closeRedPopup
        });

        return _lyr;
      },
      onEachFeature: function(feature, layer) {
        layer.addTo(clusterGroup)
      }
    });
    //clusterGroup.addLayer(geoJsonLayer);

    return clusterGroup;

    function setRedBigIcon(e:any) {
      var layer = e.target;
      layer.setIcon(e.target.options.icon = bigRedIcon);
    }

    function setBlueBigIcon(e:any) {
      var layer = e.target;
      layer.setIcon(e.target.options.icon = bigSkyIcon);
    }

    function setGreenBigIcon(e:any) {
      var layer = e.target;
      layer.setIcon(e.target.options.icon = bigGreenIcon);
    }

    function setBlueIcon(e:any) {
      var layer = e.target;
      if (!layer._map._popup) {
        //CHANGE ICON ACCORDING TO NUMBER OF ACTIVE WARNINGS
        layer.setIcon(layer.options.icon = skyIcon);
      }
    }

    function setGreenIcon(e:any) {
      var layer = e.target;
      if (!layer._map._popup) {
        //CHANGE ICON ACCORDING TO NUMBER OF ACTIVE WARNINGS
        layer.setIcon(layer.options.icon = optimalIcon);
      }
    }

    function setRedIcon(e:any) {
      var layer = e.target;
      if (!layer._map._popup) {
        //CHANGE ICON ACCORDING TO NUMBER OF ACTIVE WARNINGS
        layer.setIcon(layer.options.icon = dangerIcon);
      }
    }

    function clickedBlueIcon(e:any) {
      var layer = e.target;

      if (activeMarker) {
        //CHANGE ICON ACCORDING TO NUMBER OF ACTIVE WARNINGS
        activeMarker.setIcon(layer.options.icon = skyIcon);
      }
      //lrouter.navigate(['/main/stations']);
      layer.setIcon(layer.options.icon = bigSkyIcon);
      activeMarker = layer;
    }

    function clickedGreenIcon(e:any) {
      var layer = e.target;

      if (activeMarker) {
        //CHANGE ICON ACCORDING TO NUMBER OF ACTIVE WARNINGS
        activeMarker.setIcon(layer.options.icon = optimalIcon);
      }
      //lrouter.navigate(['/main/stations']);
      layer.setIcon(layer.options.icon = bigGreenIcon);
      activeMarker = layer;
    }

    function clickedRedIcon(e:any) {
      var layer = e.target;

      if (activeMarker) {
        //CHANGE ICON ACCORDING TO NUMBER OF ACTIVE WARNINGS
        activeMarker.setIcon(layer.options.icon = dangerIcon);
      }
      //lrouter.navigate(['/main/stations']);
      layer.setIcon(layer.options.icon = bigRedIcon);
      activeMarker = layer;
    }

    function closeGreenPopup(e:any) {
      if(activeMarker) {
        //CHANGE ICON ACCORDING TO NUMBER OF ACTIVE WARNINGS
        activeMarker.setIcon(activeMarker.options.icon = optimalIcon);
        activeMarker = null;
      }
    }

    function closeRedPopup(e:any) {
      if(activeMarker) {
        //CHANGE ICON ACCORDING TO NUMBER OF ACTIVE WARNINGS
        activeMarker.setIcon(activeMarker.options.icon = dangerIcon);
        activeMarker = null;
      }
    }

    function closeBluePopup(e:any) {
      if(activeMarker) {
        //CHANGE ICON ACCORDING TO NUMBER OF ACTIVE WARNINGS
        activeMarker.setIcon(activeMarker.options.icon = skyIcon);
        activeMarker = null;
      }
    }
  }
}
