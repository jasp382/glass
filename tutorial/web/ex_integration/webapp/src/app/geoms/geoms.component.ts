import { Component, OnInit } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Layers, Geometry } from '../interfaces';

import { RestlyrService } from '../services/restlyr.service';
import { GeosService } from '../services/geos.service';

export interface MapCols {
  code: string,
  classn: string
}


@Component({
  selector: 'app-geoms',
  templateUrl: './geoms.component.html',
  styleUrls: ['./geoms.component.css']
})
export class GeomsComponent implements OnInit {

  layers: Layers[]  = [];
  geoms: Geometry[] = [];

  layer: Layers|null = null;

  shapeCols: MapCols = {code: '', classn: ''};

  fileName: string = '';

  files: File[] = [];

  constructor(
    private http: HttpClient,
    private lyrServ: RestlyrService,
    private geoServ: GeosService
  ) { }

  ngOnInit(): void {
    this.lyrServ.getLayers().subscribe(layers => {
      this.layers = layers;
    });
    
  }

  selectLayer(lyr: Layers) {
    this.layer = lyr;

    this.geoServ.getGeoms(lyr.id).subscribe(geoms => {
      this.geoms = geoms;
    });
  };

  onFileSelected(event: any) {
    this.files = event.target.files;

    if (this.files) {
      this.fileName = this.files[0].name;
    }
  };

  addGeos(): void {
    const formData = new FormData();

    for (var i = 0; i < this.files.length; i++) { 
      formData.append("shape[]", this.files[i]);
    }

    formData.append('code', this.shapeCols.code);
    formData.append('class', this.shapeCols.classn);

    if (this.files.length) {

      const upload$ = this.http.post(
        'http://localhost:8000/layerdata/' + String(this.layer!.id) + '/',
        formData
      );

      upload$.subscribe(rsp => {
        this.geoServ.getGeoms(this.layer!.id).subscribe(geoms => {
          this.geoms = geoms;
        });
      
      });
    }
  };

  delGeoms(lyrid: number) {
    this.geoms = [];

    this.geoServ.delGeoms(lyrid).subscribe();
  };

}
