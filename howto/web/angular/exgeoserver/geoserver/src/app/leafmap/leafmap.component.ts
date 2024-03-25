import { Component, AfterViewInit } from '@angular/core';

import { HttpClient } from '@angular/common/http';
import * as L from 'leaflet';
import "leaflet.markercluster";

export interface VectLegend {
  name: string,
  title: string,
  filter: string,
  symbolizers: [{
    Polygon : {
      fill: string,
      "fill-opacity": string
    }
  }]
}

export interface Legend {
  label: string,
  quantity: string,
  color: string,
  opacity: string
}

export interface WmsLayer {
  layer: string,
  workspace: string,
  style?: string,
  service?: any,
  gtype: string,
  leg?: Legend[]
}

export interface Layers {
  name: string,
  layer: any,
  active: boolean
}

@Component({
  selector: 'app-leafmap',
  templateUrl: './leafmap.component.html',
  styleUrls: ['./leafmap.component.css']
})
export class LeafmapComponent implements AfterViewInit {

  private map: any;

  wmsurl = 'http://localhost:8000/api/wms/pwgis?';
  exturl = 'http://localhost:8000/api/extent/pwgis/uacoimbra/';
  pnturl = 'http://localhost:8000/api/wfs/pwgis/osm_points/?count=1000';
  mtway  = 'http://localhost:8000/api/wfs/pwgis/osm_roads/?val=motorway&attr=highway';
  priurl = 'http://localhost:8000/api/wfs/pwgis/osm_roads/?val=primary&attr=highway';
  legurl  = 'http://localhost:8000/api/multileg/pwgis/?' + 
    'layers=dem_coimbra,uacoimbra&' +
    'styles=dem_style,ua2012';

  wmsLayers: WmsLayer[] = [{
    layer: 'uacoimbra', workspace: 'pwgis',
    style: 'ua2012', gtype: 'polygon'
  }, {
    layer: 'dem_coimbra', workspace: 'pwgis',
    style: 'dem_style', gtype: 'raster'
  }];

  layers: Layers[] = [];

  isLeg: boolean = false;

  private initMap(): void {
    this.map = L.map('map', {
      center: [39.5, -8.5],
      zoom: 7
    });

    const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      minZoom: 3,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    });

    tiles.addTo(this.map);
  };

  private addWmsLayers(): void {
    for (let lyr of this.wmsLayers) {
      lyr.service = L.tileLayer.wms(this.wmsurl, {
        layers: lyr.layer,
        format: 'image/png',
        transparent: true,
        styles: lyr.style!
      });

      this.map.addLayer(lyr.service);

      this.layers.push({
        name: lyr.layer,
        layer: lyr.service,
        active: true
      });
    }
  }

  getGeoServerData(url: string) {
    return this.http.get(url);
  }

  private setMapExtent(): void {
    this.getGeoServerData(this.exturl).subscribe((r: any) => {
      let ext = r;

      let topleft = L.latLng(ext['max_y'], ext['min_x']),
          lowerright = L.latLng(ext['min_y'], ext['max_x']);

      let bounds = L.latLngBounds(topleft, lowerright);

      this.map.fitBounds(bounds);
    });
  }

  private addPoints(): void {
    this.getGeoServerData(this.pnturl).subscribe((gjson: any) => {
      var baseLyr = L.markerClusterGroup();

      var gjsonlyr = L.geoJSON(gjson, {
        pointToLayer: function (feature, latlng) {
          var f_icon = L.icon({
            iconUrl: '/assets/map-pin.svg',
            iconSize: [25, 30],
            iconAnchor: [12.5, 30],
            popupAnchor: [0, -30]
          });

          var feat = L.marker(latlng, {icon: f_icon});

          var str_popup = "<b style='color:DeepSkyBlue;'>OSM Points</b><br>";
	
	        var feat_html;
	
	        for (var field in feature.properties) {
		        if (feature.properties.hasOwnProperty(field)) {
			        if (!feature.properties[field]) {
				        feat_html = 'null';
			        } else if (String(feature.properties[field]).substring(0,4) === 'http') {
				        feat_html = "<a href='" + feature.properties[field] + "' target='_blank'>Click</a>";
			        } else {
				        feat_html = feature.properties[field];
			        }
			
			        str_popup += "<b>" + field + ": </b>" +
				        feat_html +
				      "<br>";
		        }
	        }

          feat.bindPopup(str_popup);

          return feat;
        },
        onEachFeature: function (feat, lyr) {
          lyr.addTo(baseLyr);
        }
      });

      this.map.addLayer(baseLyr);

      this.layers.push({
        name: 'OSM Points',
        layer: baseLyr,
        active: true
      });
    });
  }

  private addRoads(layer_name: string) {
    function getColor(d: string) {
      return d === 'motorway' ? 'black' : 'blue';
    };

    let url = layer_name === 'motorway' ? this.mtway : this.priurl;

    this.getGeoServerData(url).subscribe((gjson: any) => {
      var lyr = L.geoJSON(gjson, {
        style: function set_style(feature) {
          return {
            opacity: 1,
            color: getColor(feature!.properties.highway)
          }
        }
      });

      this.map.addLayer(lyr);

      this.layers.push({
        name: 'OSM ' + layer_name,
        layer: lyr,
        active: true
      });
    });
  }

  private addLegend() {
    this.getGeoServerData(this.legurl).subscribe((leg: any) => {
      console.log(leg);

      // Iterate over all layers
      for (let lyr of this.wmsLayers) {
        for (let _leg of leg) {
          if (_leg.Legend[0].layerName === lyr.layer) {
            lyr.leg = []
            if (lyr.gtype === 'raster') {
              let legentries: Legend[] = _leg.Legend[0].rules[0].symbolizers[0].Raster.colormap.entries;
              for (let _i=0; _i < legentries.length; _i++) {
                lyr.leg.push({
                  label : legentries[_i].label,
                  quantity: legentries[_i].quantity,
                  color: legentries[_i].color.toLowerCase(),
                  opacity: legentries[_i].opacity
                });
              };
            } else {
              let legentries: VectLegend[] = _leg.Legend[0].rules;
              for (let _i=0; _i < legentries.length; _i++) {
                lyr.leg.push({
                  label: legentries[_i].title,
                  quantity: '',
                  color: legentries[_i].symbolizers[0].Polygon.fill.toLowerCase(),
                  opacity: legentries[_i].symbolizers[0].Polygon['fill-opacity']
                });
              }
            }

            break;
          }
        }
      }
      this.isLeg = true;
      console.log(this.wmsLayers);
    })
  }

  constructor(
    private http: HttpClient
  ) { }

  ngAfterViewInit(): void {
    this.initMap();

    this.addWmsLayers();

    this.setMapExtent();

    this.addPoints();

    this.addRoads('motorway');
    this.addRoads('primary');

    this.addLegend();
  }

  activeLayer(l: Layers) {
    if (!l.active) {
      this.map.removeLayer(l.layer);
    } else {
      this.map.addLayer(l.layer);
    }
  }

}
