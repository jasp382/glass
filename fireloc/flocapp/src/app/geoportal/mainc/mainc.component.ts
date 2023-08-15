import { Component, OnInit } from '@angular/core';

import { faCaretRight, faCaretLeft } from '@fortawesome/free-solid-svg-icons';

// Interfaces and Constants
import { Token } from 'src/app/interfaces/login';
import { LeafletLayer, MapSettings } from 'src/app/interfaces/maps';
import { ClusterLayer, ViewContributionGroup } from 'src/app/interfaces/layers';
import { FirelocClusterLayer } from 'src/app/interfaces/layers';
import { Extent } from 'src/app/constants/mapext';

// Leaflet
import * as L from 'leaflet';

// Services
import { MarkerService } from 'src/app/serv/leafmap/marker.service';
import { LyrsService } from 'src/app/serv/leafmap/lyrs.service';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as leafSelect from '../../stores/leaf/leaf.reducer';
import * as leafActions from '../../stores/leaf/leaf.actions';
import * as cLyrActions from '../../stores/clusterlyr/clyr.actions';
import * as cLyrSelect from '../../stores/clusterlyr/clyr.reducer';
import * as logSelect from '../../stores/login/login.reducer';

// util
import { pointsToWKTF } from 'src/app/util/formatter';

/**
 * Geoportal Main component.
 * 
 * Displays the content for the left menu, geoportal map, right menu, and map footer with date range slider.
 * Left menu contains geospatial layers, legend for said layers and different map base layers.
 * Right menu contains FireLoc events, FireLoc contributions, all events, and graphs.
 * 
 */
@Component({
  selector: 'app-mainc',
  templateUrl: './mainc.component.html',
  styleUrls: ['./mainc.component.css']
})
export class MaincComponent implements OnInit {

  token : Token|null = null;

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
  clusterLayers: ClusterLayer[] = [];

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
  markerClusterGroup!: L.MarkerClusterGroup;

  isClusterLoading: boolean = true;

  isMainLayerActive: boolean = false;

  ctbLayers: LeafletLayer = {};

  /**
   * Constructor for the Geoportal Main front component. Initializes the user's logged status.
   * @param authServ authentication service. See {@link AuthService}.
   * @param contribLayersServ contribution layers service. See {@link ContributionLayersService}.
   * @param markerServ map markers service. See {@link MarkerService}.
   * @param mapLayerServ map layers service. See {@link LyrsService}.
   */
  constructor(
    private store: Store<AppState>,
    //private authServ: AuthService,
    //private contribLayersServ: ContributionLayersService,
    private markerServ: MarkerService,
    private mapLayerServ: LyrsService,
  ) { }//this.isLoggedIn = this.authServ.isLoggedIn(); }

  /**
   * Checks user permissions and initializes the contributions marker cluster group for the Geoportal map.
   * 
   * If user is logged in and has permissions, also requests the API to get the contribution layers from the API.
   */
  ngOnInit(): void {
    // contribution layers map cluster
    this.markerClusterGroup = L.markerClusterGroup({ removeOutsideVisibleBounds: true });

    // Get Cluster Layers
    this.store
      .select(cLyrSelect.getCusterLayers)
      .subscribe((lyr: ClusterLayer[]) => {
        if (!lyr.length) {
          this.store
            .select(logSelect.getLoginToken)
            .subscribe((pload: Token|null) => {
              let token: Token|null = pload;
              
              if (token !== null) {
                this.store.dispatch(cLyrActions.GetClusterLayer({payload: token}))
              }
            });
        } else if (lyr.length && this.isClusterLoading) {
          this.clusterLayers = lyr;

          for (let _l of this.clusterLayers) {
            if (_l.level === 1) {
              this.store
                .select(logSelect.getLoginToken)
                .subscribe((pload: Token|null) => {
                  let token: Token|null = pload;
              
                if (token !== null) {
                  this.store.dispatch(cLyrActions.ClusterWFS({payload: {
                    token: token, ws: _l.workspace, lyr: _l.gsrvlyr
                  }}));

                  this.store.dispatch(cLyrActions.IdCluster({payload: _l}));

                  this.isClusterLoading = false;
                }
                })
              break;
            }
          }

        } else {
          this.clusterLayers = lyr;

          // Create Leaflet Layer if geojson available
          for (let _l of this.clusterLayers) {
            if (_l.leaflyr && _l.geojson !== null && this.map) {
              if (this.isMainLayerActive) {
                this.mapLayerServ.removeLayer(this.map, this.markerClusterGroup);
              }

              // create map layer
              this.markerClusterGroup = this.markerServ.addGeoLayerToCluster(_l.geojson);
              
              // add cluster to map
              if (this.isMainLayerActive) {
                this.mapLayerServ.addLayer(this.map, this.markerClusterGroup);
              }

              break;
            }
          }
        }
      });
    
    // Get token state
    this.store
      .select(logSelect.getLoginToken)
      .subscribe((payload: Token|null) => {
        this.token = payload;
      })
    
    // Get Main Cluster Layer Status
    this.store
      .select(cLyrSelect.custerIsActive)
      .subscribe((payload: boolean) => {
        this.isMainLayerActive = payload;

        if (!this.isMainLayerActive && this.map) {
          this.mapLayerServ.removeLayer(this.map, this.markerClusterGroup);
        } else {
          for (let _l of this.clusterLayers) {
            if (_l.leaflyr && this.map) {
              this.markerClusterGroup = this.markerServ.addGeoLayerToCluster(_l.geojson);
              // add cluster to map
              this.mapLayerServ.addLayer(this.map, this.markerClusterGroup);

              break;
            }
          }
        }
      });
    
    // Get Contributions Layer Groups
    this.store
      .select(leafSelect.getContribLayers)
      .subscribe((payload: ViewContributionGroup[]) => {
        for (let group of payload) {
          for (let glyr of group.layers) {
            if (glyr.active && !glyr.inMap) {
              let leafLayer: any = this.mapLayerServ.wmsLayer(
                glyr.work, glyr.layer,
                glyr.style === null ? 'default' : glyr.style
              );

              this.ctbLayers[glyr.slug] = leafLayer;

              if (this.map) {
                this.mapLayerServ.addLayer(this.map, leafLayer);
              }
            }
          }
        }
      });
  }

  /**
   * Opens or closes the left menu with geospatial layers and legend content
   */
  toggleLeftPanel() { this.isLeftOpen = !this.isLeftOpen; }

  /**
   * Change basemap
   */
  changeBasemap(newMap: string) {
    this.store.dispatch(leafActions.UpdateBasemap({payload: newMap}));
  }
  
  /**
   * Receives the geoportal map from child component.
   * Sets listeners for zoom change and visible are change.
   * @param map <
   */
  receiveMap(map: any) {
    this.map = map;
    // set listeners
    this.getContribLayerZoom();
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
   * Gets contribution layer for map according to current map zoom and bounds
   */
  getContribLayerZoom() {
    // get contribution layer according to zoom and bounding box
    for (let index = 0; index < this.clusterLayers.length; index++) {
      let layer = this.clusterLayers[index];

      if (this.token !== null && this.mapCurrentZoom && this.mapCurrentZoom >= layer.minzoom && this.mapCurrentZoom <= layer.maxzoom) {
        let _ws = layer.workspace,
            _lyr = layer.gsrvlyr;
        
        // first level does not require bounds filter
        if (layer.level === 1) {
          this.store.dispatch(cLyrActions.ClusterWFS({payload: {
            token: this.token, ws: _ws, lyr: _lyr
          }}));

          this.store.dispatch(cLyrActions.IdCluster({payload: layer}));
        } else {
          // get map bounding box
          if (this.mapBoundsWKT === undefined) this.getMapBounds();

          if (this.mapBoundsWKT) {
            this.store.dispatch(cLyrActions.ClusterWFSBBOX({payload : {
              token: this.token, ws: _ws, lyr: _lyr, bbox: this.mapBoundsWKT
            }}));

            this.store.dispatch(cLyrActions.IdCluster({payload: layer}));
          }
        }
        break;
      }
    }
  }
}
