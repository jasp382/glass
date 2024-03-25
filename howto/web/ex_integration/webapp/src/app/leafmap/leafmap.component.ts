import { Component, AfterViewInit } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import * as L from 'leaflet';

import { Layers, LayersVis } from '../interfaces';

import { RestlyrService } from '../services/restlyr.service';

@Component({
  selector: 'app-leafmap',
  templateUrl: './leafmap.component.html',
  styleUrls: ['./leafmap.component.css']
})
export class LeafmapComponent implements AfterViewInit {

  private map: any;

  layers: LayersVis[] = [];

  wmsurl: string = 'http://localhost:8000/geoserver/wms/pwgis?';
  exturl: string = 'http://localhost:8000/geoserver/extent/pwgis/';

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

  private addWmsLayers(layers: Layers[]): void {
    for (let lyr of layers) {
      let layer: LayersVis = {
        wmsname: 'layer_' + lyr.id,
        name: lyr.design,
        layer: L.tileLayer.wms(this.wmsurl, {
          layers: 'layer_' + lyr.id,
          format: 'image/png',
          transparent: true,
          styles: lyr.style ? lyr.style : ''
        }),
        active: true
      };

      this.map.addLayer(layer.layer);

      this.layers.push(layer);
    }
  }

  getGeoServerData(url: string) {
    return this.http.get(url);
  }

  private setMapExtent(wms: string): void {
    let url = this.exturl + wms + '/';
    this.getGeoServerData(url).subscribe((r: any) => {
      let ext = r;

      let topleft = L.latLng(ext['max_y'], ext['min_x']),
          lowerright = L.latLng(ext['min_y'], ext['max_x']);

      let bounds = L.latLngBounds(topleft, lowerright);

      this.map.fitBounds(bounds);
    });
  }

  constructor(
    private lyrServ: RestlyrService,
    private http: HttpClient
  ) { }

  ngAfterViewInit(): void {
    console.log(this.layers);
    this.initMap();

    this.lyrServ.getLayers().subscribe(layers => {
      this.addWmsLayers(layers);

      if (this.layers.length) {
        this.setMapExtent(this.layers[0].wmsname);
      }
    });
  }

  activeLayer(l: LayersVis) {
    if (!l.active) {
      this.map.removeLayer(l.layer);
    } else {
      this.map.addLayer(l.layer);
    }
  }

}
