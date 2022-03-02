import { Component, AfterViewInit } from '@angular/core';
import * as L from 'leaflet';
import { LeafletConstants } from '../../common/leaflet-constants';

import { LyrextentService } from '../services/gsrv/lyrextent.service';
import { Ext } from '../models/gsrv/ext';

@Component({
  selector: 'app-wge',
  templateUrl: './wge.component.html',
  styleUrls: ['../serv.component.css']
})
export class WgeComponent implements AfterViewInit {
  work : string = 'cos';
  lyr  : string = 'cos_18_l4_v2';
  style : string = 'cos_18_l4';
  ext = {} as Ext;
  exts: Ext[];

  private map;

  constructor(private extService : LyrextentService) { }

  setExtent() {
    this.extService.getExtent(this.work, this.lyr).subscribe((ext: Ext) => {
      this.ext = ext;

      var tl = L.latLng(this.ext['max_y'],this.ext['min_x']);
      var lr = L.latLng(this.ext['min_y'], this.ext['max_x']);

      var bounds = L.latLngBounds(tl, lr);

      this.map.fitBounds(bounds);
    })
  }

  private initMap(): void {
    this.map = L.map('map', {
      center      : [39.6818, -7.96643],
      zoom        : 3,
      minZoom     : 1,
      maxZoom     : 20,
      zoomControl : false
    });

    // Add Scale
    L.control.scale({ position: 'bottomright' }).addTo(this.map);

    // Set Maximum bounds

    // Set Basemap
    const basemap_lyr = L.tileLayer(LeafletConstants.MAPBOX_KEY, {
      maxZoom     : 20,
      attribution : LeafletConstants.MAPBOX_STREETS_ATTRIBUTION,
      id          : LeafletConstants.MAPBOX_STREETS_ID
    });

    basemap_lyr.addTo(this.map);

    // Add tile layer
    //var url = 'http://fireloc.mat.uc.pt:8080/geoserver/cos/wms/';
    var url = 'http://127.0.0.1:8000/api/geosrv/wms/' + this.work + '/';
    var wmslyr = L.tileLayer.wms(url, {
      layers: this.lyr,
      format : 'image/png',
      transparent : true,
      styles : this.style
    });

    wmslyr.addTo(this.map);
  }

  ngAfterViewInit(): void {
    this.initMap();

    this.setExtent();
  }

}
