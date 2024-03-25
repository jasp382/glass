import { Component, OnInit } from '@angular/core';

import { NgForm } from '@angular/forms';

import { Layers, StyleData } from '../interfaces';

import { RestlyrService } from '../services/restlyr.service';

@Component({
  selector: 'app-layers',
  templateUrl: './layers.component.html',
  styleUrls: ['./layers.component.css']
})
export class LayersComponent implements OnInit {

  layers: Layers[] = [];

  layer: Layers|null = null;

  newLayer: Layers = {
    id: 0, alias: '', design: '', islayer: false,
    style: '', classes: []
  };

  addStyleActive: boolean = false;

  constructor(
    private lyrServ: RestlyrService
  ) { }

  ngOnInit(): void {
    this.lyrServ.getLayers().subscribe(layers => {
      console.log(layers);
      this.layers = layers;
    });
  }

  addLayer() {
    this.lyrServ.addLayer(this.newLayer)
      .subscribe(nLyr => {
        this.layers.push(nLyr);
      });
  };

  delLayer(_id: number) {
    this.layers = this.layers.filter((filter) => filter.id !== _id);

    this.lyrServ.delLayer(_id).subscribe();
  };

  geoserverLayer(_id:number) {
    this.lyrServ.addGeoServerLayer(_id).subscribe(rsp => {
      console.log(rsp);
    });
  }

  toggleAddStyle(lyrid: number) {
    this.addStyleActive = !this.addStyleActive ? true : false;

    this.layer = this.layers.filter((l: Layers) => l.id === lyrid)[0];
  };

  addStyle(e: NgForm) {
    let styleData: StyleData = {
      classes: [], blue: [], red: [],
      green: []
    };

    for (let i=0; i < this.layer!.classes!.length; i++) {
      styleData.classes.push(this.layer!.classes![i]);
      styleData.red.push(Number(e.value['red_' + i]));
      styleData.blue.push(Number(e.value['blue_' + i]));
      styleData.green.push(Number(e.value['green_' + i]));
    };

    console.log(styleData);

    this.lyrServ.addGeoServerStyle(this.layer!.id, styleData)
      .subscribe(rsp => {
        console.log(rsp);
        this.addStyleActive = false;
      });
  }

}
