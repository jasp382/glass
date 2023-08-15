import { Component, OnInit } from '@angular/core';
import { faCaretRight, faCaretLeft } from '@fortawesome/free-solid-svg-icons';

// Interfaces and Constants
import { MapLayer, MapSettings } from 'src/app/interfaces/maps';
import { Extent } from 'src/app/constants/mapext';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';
import { ContributionLayersService } from 'src/app/serv/rest/geo/contribution-layers.service';
import { MarkerService } from 'src/app/serv/leafmap/marker.service';
import { LyrsService } from 'src/app/serv/leafmap/lyrs.service';

// Leaflet
import * as L from 'leaflet';

// util
import { pointsToWKTF } from 'src/app/util/formatter';
import { checkUserHasPermissions } from 'src/app/util/helper';

/**
 * Geoportal Main component.
 * 
 * Displays the content for the left menu, geoportal map, right menu, and map footer with date range slider.
 * Left menu contains geospatial layers, legend for said layers and different map base layers.
 * Right menu contains FireLoc events, FireLoc contributions, all events, and graphs.
 * 
 */
@Component({
  selector: 'app-mainfront',
  templateUrl: './mainfront.component.html',
  styleUrls: ['./mainfront.component.css']
})
export class MainfrontComponent implements OnInit {

  /**
   * right arrow icon to open left geoportal menu
   */
  arrowRight = faCaretRight;
  /**
   * left arrow icon to close left geoportal menu
   */
  arrowLeft = faCaretLeft;

  /**
   * flag to determine if geoportal left menu is open or collapsed
   */
  isLeftOpen: boolean = true;

  // user checks
  /**
   * flag to determine the user's logged status
   */
  isLoggedIn: boolean = false;
  /**
   * flag to determine the user's permissions status
   */
  hasPermission = false;

  /**
   * current active tab on geoportal's right menu
   */
  activeRightTab: number = 0;

  /**
   * flag to determine if the contributions list being displayed contains all contributions or just user contributions
   */
  showingAllContribs: boolean = false;

  /**
   * list of contribution layers to get contribution clusters for geoportal map
   */
  mapContribLayers: MapLayer[] = [];

  /**
   * geoportal map settings
   */
  mapsettings: MapSettings = {
    domElem: "main-map",
    mapContainer: "mainMap",
    minZoom: 0,
    maxZoom: 19,
    scale: true,
    zoomCtrl: true,
    bounds: Extent.bounds,
    fullext: Extent.maxBounds,
    wfs: [],
    wms: []
  };
  /**
   * reference to geoportal map
   */
  map: L.Map | null = null;
  /**
   * current geoportal map zoom value
   */
  mapCurrentZoom: number | undefined;
  /**
   * current geoportal map bounds for visible map area in Well Known Text format
   */
  mapBoundsWKT: string | undefined;

  /**
   * map contributions cluster data
   */
  contribMarkerClusterGroup!: L.MarkerClusterGroup;

  /**
   * Constructor for the Geoportal Main front component. Initializes the user's logged status.
   * @param authServ authentication service. See {@link AuthService}.
   * @param contribLayersServ contribution layers service. See {@link ContributionLayersService}.
   * @param markerServ map markers service. See {@link MarkerService}.
   * @param mapLayerServ map layers service. See {@link LyrsService}.
   */
  constructor(
    private authServ: AuthService,
    private contribLayersServ: ContributionLayersService,
    private markerServ: MarkerService,
    private mapLayerServ: LyrsService,
  ) { this.isLoggedIn = this.authServ.isLoggedIn(); }

  /**
   * Checks user permissions and initializes the contributions marker cluster group for the Geoportal map.
   * 
   * If user is logged in and has permissions, also requests the API to get the contribution layers from the API.
   */
  ngOnInit(): void {
    // check user permissions
    this.hasPermission = checkUserHasPermissions(this.isLoggedIn);

    // contribution layers map cluster
    this.contribMarkerClusterGroup = L.markerClusterGroup({ removeOutsideVisibleBounds: true });

    if (this.isLoggedIn && this.hasPermission) {
      // get all contribution layers for Map Service
      this.requestContribLayers();
    }
  }

  /**
   * Opens or closes the left menu with geospatial layers and legend content
   */
  toggleLeftPanel() { this.isLeftOpen = !this.isLeftOpen; }

  // TODO CHANGE MAP STYLE
  /**
   * @ignore unused method
   */
  mapStyle1() { /* console.log("Clicked Map Style 1"); */ }
  /**
   * @ignore unused method
   */
  mapStyle2() { /* console.log("Clicked Map Style 2"); */ }
  /**
   * @ignore unused method
   */
  mapStyle3() { /* console.log("Clicked Map Style 3"); */ }
  /**
   * @ignore unused method
   */
  mapStyle4() { /* console.log("Clicked Map Style 4"); */ }

  /**
   * Gets all contribution layer services from API. 
   * These services are used to get the contributions data clusters to be displayed in the Geoportal map.
   */
  requestContribLayers() {
    this.contribLayersServ
      .getContribLayers()
      .subscribe((result: any) => { this.getMapContribLayersData(result.data); }, error => { });
  }

  /**
   * Gets the contribution layer clusters data from the API result
   * @param rawData list of layers from the API response
   */
  getMapContribLayersData(rawData: any[]) {
    this.mapContribLayers = [];
    rawData.forEach(layer => {
      let newLayer: MapLayer = {
        id: layer.id,
        slug: layer.slug,
        designation: layer.designation,
        workspace: layer.workspace,
        store: layer.store,
        level: layer.level,
        serverLayer: layer.gsrvlyr,
        minZoom: layer.minzoom,
        maxZoom: layer.maxzoom
      };
      this.mapContribLayers.push(newLayer);
    });
  }

  /**
   * Receives the geoportal map from child component.
   * Sets listeners for zoom change and visible are change.
   * @param map <
   */
  receiveMap(map: any) {
    this.map = map;
    // set listeners
    this.map?.on('zoomend', () => this.getMapZoom());
    this.map?.on('moveend', () => this.getMapBounds());
  }

  /**
   * Gets the current bounds of the visible map area and update the contribution layer clusters
   */
  getMapBounds() {
    let north = this.map?.getBounds().getNorth();
    let south = this.map?.getBounds().getSouth();
    let west = this.map?.getBounds().getWest();
    let east = this.map?.getBounds().getEast();

    let topLeft = [north, west];
    let topRight = [north, east];
    let bottomRight = [south, east];
    let bottomLeft = [south, west];

    let points = [topLeft, topRight, bottomRight, bottomLeft, topLeft];
    this.mapBoundsWKT = pointsToWKTF(points);

    // get contribution layer according to current zoom and map bounds
    this.getContribLayerZoom();
  }

  /**
   * Gets current map zoom and update the contribution layer clusters
   */
  getMapZoom() {
    this.mapCurrentZoom = this.map?.getZoom();
    // get contribution layer according to current zoom and map bounds
    this.getContribLayerZoom();
  }

  /**
   * Gets current tab opened in the Geoportal right menu.
   * If a tab different than 'Contributions' is open, clears the contribution clusters from the map.
   * @param activeTab 
   */
  receiveActiveRightTab(activeTab: number) {
    this.activeRightTab = activeTab;

    // if there is an open tab different than contributions, clear contrib clusters
    if (this.activeRightTab !== 2 && this.activeRightTab !== 0 && this.map)
      this.mapLayerServ.removeLayer(this.map, this.contribMarkerClusterGroup);
  }

  /**
   * Receive contributions option from child component. 
   * @param isAllContrib true if all contributions are displayed, false if otherwise
   */
  receiveContribOption(isAllContrib: boolean) {
    this.showingAllContribs = isAllContrib;

    // get contribution layer according to current zoom and map bounds
    if (this.mapCurrentZoom === undefined) this.getMapZoom();
  }

  /**
   * Gets contribution layer for map according to current map zoom and bounds
   */
  getContribLayerZoom() {
    // get contribution layer according to zoom and bounding box
    for (let index = 0; index < this.mapContribLayers.length; index++) {
      let layer = this.mapContribLayers[index];

      if (this.mapCurrentZoom && this.mapCurrentZoom >= layer.minZoom && this.mapCurrentZoom <= layer.maxZoom) {
        let workspace = layer.workspace;
        let serverLayer = layer.serverLayer;

        // first level does not require bounds filter
        if (layer.level === 1) {
          this.getContribLayer(workspace, serverLayer);
        }
        else {
          // get map bounding box
          if (this.mapBoundsWKT === undefined) this.getMapBounds();
          this.getContribLayer(workspace, serverLayer, this.mapBoundsWKT);
        }
        ;
      }
    }
  }

  /**
   * Gets contribution clusters data for Geoportal map.
   * @param layerWorkspace contribution layer workspace for Geo Server
   * @param serverLayer contributin layer name for Geo Server
   * @param boundingBox optional bounding box to filter for visible map area
   */
  getContribLayer(layerWorkspace: string, serverLayer: string, boundingBox?: string) {
    // get contribution clusters with map bounds
    if (boundingBox) {
      this.contribLayersServ.getWebFeatureService(layerWorkspace, serverLayer, boundingBox).subscribe(
        (result: any) => {
          // clear layer
          if (this.map) {
            this.mapLayerServ.removeLayer(this.map, this.contribMarkerClusterGroup);
            this.contribMarkerClusterGroup = L.markerClusterGroup();
          }
          // get geojson data
          let geoJsonData = result.data;
          // create map layer
          this.markerServ.addGeoLayerToCluster(geoJsonData, this.contribMarkerClusterGroup);
          // add cluster to map
          if (this.map)
            this.mapLayerServ.addLayer(this.map, this.contribMarkerClusterGroup);
        }, error => { }
      );
    }
    // get contribution clusters without map bounds
    else {
      this.contribLayersServ.getWebFeatureService(layerWorkspace, serverLayer).subscribe(
        (result: any) => {
          // clear layer
          if (this.map) {
            this.mapLayerServ.removeLayer(this.map, this.contribMarkerClusterGroup);
            this.contribMarkerClusterGroup = L.markerClusterGroup();
          }
          // get geojson data
          let geoJsonData = result.data;
          // create map layer
          this.markerServ.addGeoLayerToCluster(geoJsonData, this.contribMarkerClusterGroup);
          // add cluster to map
          if (this.map)
            this.mapLayerServ.addLayer(this.map, this.contribMarkerClusterGroup);
        }, error => { }
      );
    }
  }

}
