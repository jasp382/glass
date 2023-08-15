import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import * as L from 'leaflet';
import { Extent } from 'src/app/constants/mapext';
import { MapSettings } from 'src/app/interfaces/maps';

import { MapsService } from './maps.service';

@Component({ template: `<div id='map'></div>` })
class DummyComponent { }

describe('TS65 MapsService', () => {
  let service: MapsService;
  let mapSettings: MapSettings;
  let fixture: ComponentFixture<DummyComponent>;
  let component: DummyComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DummyComponent]
    }).compileComponents();

    service = TestBed.inject(MapsService);
    fixture = TestBed.createComponent(DummyComponent);
    component = fixture.componentInstance;

    mapSettings = {
      domElem: "map",
      mapContainer: "map",
      minZoom: 0,
      maxZoom: 19,
      scale: false,
      zoomCtrl: true,
      bounds: Extent.bounds,
      fullext: Extent.maxBounds,
      wfs: [],
      wms: []
    }
  });

  it('T65.1 should be created', () => { expect(service).toBeTruthy(); });

  it('T65.2 should create a map with provided settings', () => {
    let createSpy = spyOn(service, 'createMap').and.callThrough();
    service.createMap(mapSettings);
    expect(createSpy).toHaveBeenCalled();
  });

  it('T65.3 should update bounds of a given a map', () => {
    let updateSpy = spyOn(service, 'updateBounds').and.callThrough();
    service.updateBounds(L.map('map'), mapSettings);
    expect(updateSpy).toHaveBeenCalled();
  });
});
