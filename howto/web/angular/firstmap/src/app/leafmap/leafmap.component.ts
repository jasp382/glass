import { Component, AfterViewInit } from '@angular/core';
import * as L from 'leaflet';

export interface Basemaps {
  layer: L.TileLayer,
  ref : string,
  active: boolean
}

@Component({
  selector: 'app-leafmap',
  templateUrl: './leafmap.component.html',
  styleUrls: ['./leafmap.component.css']
})
export class LeafmapComponent implements AfterViewInit {

  private map: any;

  token: string = 'pk.eyJ1IjoiamFzcDEyIiwiYSI6ImNqNnRwYnF3MDA0YXkycXM0M210M3FtejQifQ.KfkaOt8Xc02oPI9lBUtHrA';
  
  someBasemaps: Basemaps[] = [{
    ref: "OpenStreetMap",
    layer: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }),
    active: true
  }, {
    ref: "Mapbox Streets",
    layer: L.tileLayer(
      'https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=' + this.token,
      { maxZoom: 19, 
        attribution: 'Basemap from @ <a href="https://www.mapbox.com/">Mapbox</a>', 
        tileSize: 512, zoomOffset: -1 
      }
    ),
    active: false
  }, {
    ref: "ESRI Satellite",
    layer: L.tileLayer('http://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19, attribution: '&copy; @ESRI'
    }),
    active: false
  }, {
    ref: "Satellite",
    layer: L.tileLayer(
      'https://api.mapbox.com/v4/{id}/{z}/{x}/{y}@2x.jpg90?access_token=' + this.token,
      { maxZoom: 19,
        attribution: 'Basemap from @ <a href="https://www.mapbox.com/">Mapbox</a>',
        tileSize: 512, zoomOffset: -1, id: 'mapbox.satellite' 
      }
    ),
    active: false
  }];

  currentBasemap: Basemaps = this.someBasemaps[0];

  icon = {
    icon: L.icon({
      iconSize: [ 25, 41 ],
      iconAnchor: [ 13, 0 ],
      iconUrl: 'assets/marker-icon.png',
      shadowUrl: 'assets/marker-shadow.png'
    })
  };

  geomLayers = [{
    layer: 'Polygon', active: true, geom: L.polygon([
      [40, -9],
      [40, -8],
      [39, -8],
      [39, -9]
    ], {
      fillColor: 'blue',
      color: 'white',
      fillOpacity: 1
    })
  }, {
    layer: 'Point', active: true,
    geom: L.marker([39.5, -8.5], this.icon)
  }, {
    layer: 'line', active: true,
    geom: L.polyline([[39.5, -9], [39.5, -8]], {
      color: 'red',
      weight: 3,
      opacity: 1
    })
  }];


  private initMap(): void {
    this.map = L.map('map', {
      center: [39.5, -8.5],
      zoom: 7
    });

    this.currentBasemap.layer.addTo(this.map);

    this.geomLayers.forEach((l) => {
      l.geom.addTo(this.map)
    });
  }

  ngAfterViewInit(): void {
    this.initMap();
  }

  changeLayer(bmap: Basemaps) {
    this.map.removeLayer(this.currentBasemap.layer);

    this.currentBasemap = bmap;

    this.currentBasemap.layer.addTo(this.map);

    this.someBasemaps.forEach((bm: Basemaps) => {
      if (bm.active && bm.ref !== bmap.ref) {
        bm.active = false;
      }
    });
  }

  changeGeomLayer(l: any) {
    if (!l.active) {
      this.map.removeLayer(l.geom);
    } else {
      this.map.addLayer(l.geom);
    }
  };

}
