import { Component, OnInit, Input, Output, EventEmitter, AfterViewInit, ChangeDetectorRef } from '@angular/core';

// Leaflet
import * as L from 'leaflet';

// Interfaces
import { MapSettings } from 'src/app/interfaces/maps';

// Constants
import { Basemaps } from 'src/app/util/basemaps';

// Services
import { MapsService } from 'src/app/serv/leafmap/maps.service';
import { LyrsService } from 'src/app/serv/leafmap/lyrs.service';

/**
 * leaflet default icon for retina device
 */
const iconRetinaUrl = 'assets/marker-icon-2x.png';
/**
 * leaflet default icon
 */
const iconUrl = 'assets/marker-icon.png';
/**
 * leaflet default icon shadow
 */
const shadowUrl = 'assets/marker-shadow.png';
/**
 * create leaflet default icon with default values
 */
const iconDefault = L.icon({ //default values
  iconRetinaUrl,
  iconUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41]
});
L.Marker.prototype.options.icon = iconDefault;

/**
 * Leafmap component.
 * 
 * Displays a Leaflet map with custom settings, meant to be used as a child component.
 */
@Component({
  selector: 'app-leafmap',
  templateUrl: './leafmap.component.html',
  styleUrls: ['./leafmap.component.css']
})

export class LeafmapComponent implements OnInit, AfterViewInit {

  /**
   * custom leaflet map settings
   */
  @Input("map-settings") mapsettings!: MapSettings;
  /**
   * @ignore unused
   */
  @Input('leafletMarkerCluster') markerCluster: any;

  /**
   * emits the map to parent components for other component specific map initializations 
   */
  @Output("map") mapEmitter = new EventEmitter<any>();

  /**
   * leaflet map reference
   */
  map: any = null;

  /**
   * list of available basemap services
   */
  bmaps: string[] = Basemaps.servicesList;
  /**
   * default basemap for map
   */
  basemap: string = this.bmaps[0];

  /**
   * map HTML div element from the DOM
   */
  private mapDiv: Element | null = null;
  /**
   * resize observer to detect map changes and re-render map tiles
   */
  private mapResizeObserver!: ResizeObserver;

  /**
   * Empty constructor.
   * @param mapServ maps service. See {@link MapsService} for more information.
   * @param lyrServ map layers service. See {@link LyrsService} for more information.
   * @param changeDetector change detector
   */
  constructor(
    private mapServ: MapsService,
    private lyrServ: LyrsService,
    private changeDetector: ChangeDetectorRef
  ) { }

  /**
   * Re-renders the map if it exists.
   */
  ngOnInit(): void {
    if (this.map !== null && this.map !== undefined)
      this.map.invalidateSize();
  }

  /**
   * Creates a new map if one has not yet been created using the map service and adds a base layer with the layers service.
   * 
   * After map creation, emits the map to the parent component. 
   * It also initializes the resize observer to detect map dimensions change.
   */
  ngAfterViewInit(): void {
    if (this.map === null || this.map === undefined) {
      this.map = this.mapServ.createMap(this.mapsettings);
      this.map = this.lyrServ.updateBasemap(this.map, this.basemap);

      // emit to parent components
      this.mapEmitter.emit(this.map);
    }

    // observe for changes in map element size
    this.mapDiv = document.getElementById(this.mapsettings.mapContainer);
    this.mapResizeObserver = new ResizeObserver(() => this.resized());

    // add observable to HTML div
    if (this.mapDiv !== null) this.mapResizeObserver.observe(this.mapDiv);

    if (this.map !== null && this.map !== undefined) this.map.invalidateSize();
  }

  /**
   * Resizes map to accomodate interface changes
   */
  resized() {
    if (this.map !== null && this.map !== undefined) {
      // resize map to accomodate UI changes
      this.map.invalidateSize();
      this.changeDetector.detectChanges();
    }
  }

  /**
   * Removes observable for the map dimensions change and removes the leaflet map.
   */
  ngOnDestroy() {
    // remove observable
    if (this.mapResizeObserver !== undefined) this.mapResizeObserver.disconnect();

    // make sure the map is destroyed to be recreated on redirect
    if (this.map !== null && this.map !== undefined) this.map.remove();
  }

  /* addGeoJson(layer: L.GeoJSON) { layer.addTo(this.map); } */

  /* addWMSLayer(layer: L.TileLayer.WMS) { layer.addTo(this.map); } */

  /* addCircle(latValue: any, longValue: any) {
    var circle = L.circleMarker([latValue, longValue]);
    circle.addTo(this.map);
  } */

  /* setMapExtent(bounds: L.LatLngBounds) { this.map.fitBounds(bounds); } */

}