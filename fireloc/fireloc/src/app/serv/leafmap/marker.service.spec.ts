import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import * as L from 'leaflet';
import { firelocMarker } from 'src/app/constants/mapMarkers';

import { MarkerService } from './marker.service';

@Component({ template: `<div id='map'></div>` })
class DummyComponent { }

describe('TS66 MarkerService', () => {
  let service: MarkerService;
  let fixture: ComponentFixture<DummyComponent>;
  let component: DummyComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DummyComponent]
    }).compileComponents();

    service = TestBed.inject(MarkerService);
    fixture = TestBed.createComponent(DummyComponent);
    component = fixture.componentInstance;
  });

  it('T66.1 should be created', () => { expect(service).toBeTruthy(); });

  it('T66.2 should add marker to a given map', () => {
    let addSpy = spyOn(service, 'addMarkerToMap').and.callThrough();
    service.addMarkerToMap(L.map('map'), 1, 1);
    expect(addSpy).toHaveBeenCalled();
  });

  it('T66.3 should add custom marker to a given map', () => {
    let addSpy = spyOn(service, 'addCustomMarkerToMap').and.callThrough();
    service.addCustomMarkerToMap(L.map('map'), 1, 1, firelocMarker);
    expect(addSpy).toHaveBeenCalled();
  });

  it('T66.4 should start a new polyine group for a given map', () => {
    let startSpy = spyOn(service, 'startPolylineGroup').and.callThrough();
    let result = service.startPolylineGroup(L.map('map'));
    expect(startSpy).toHaveBeenCalled();
    expect(result).toBeDefined();
  });

  it('T66.5 should line to map after clearing polygroup for a given polygroup', () => {
    let addSpy = spyOn(service, 'addPolylineToFilterMap').and.callThrough();
    let clearSpy = spyOn(service, 'clearPolyGroup').and.callThrough();
    service.addPolylineToFilterMap([], new L.FeatureGroup);
    expect(addSpy).toHaveBeenCalled();
    expect(clearSpy).toHaveBeenCalled();
  });

  it('T66.6 should polygon to map after clearing polygroup for a given polygroup', () => {
    let addSpy = spyOn(service, 'addPolygonToFilterMap').and.callThrough();
    let clearSpy = spyOn(service, 'clearPolyGroup').and.callThrough();
    service.addPolygonToFilterMap([], new L.FeatureGroup);
    expect(addSpy).toHaveBeenCalled();
    expect(clearSpy).toHaveBeenCalled();
  });

  it('T66.7 should line to map without clearing polygroup for a given polygroup', () => {
    let addSpy = spyOn(service, 'addPolylineToMap').and.callThrough();
    let clearSpy = spyOn(service, 'clearPolyGroup').and.callThrough();
    service.addPolylineToMap([], new L.FeatureGroup);
    expect(addSpy).toHaveBeenCalled();
    expect(clearSpy).not.toHaveBeenCalled();
  });

  it('T66.8 should polygon to map without clearing polygroup for a given polygroup', () => {
    let addSpy = spyOn(service, 'addPolygonToMap').and.callThrough();
    let clearSpy = spyOn(service, 'clearPolyGroup').and.callThrough();
    service.addPolygonToMap([], new L.FeatureGroup);
    expect(addSpy).toHaveBeenCalled();
    expect(clearSpy).not.toHaveBeenCalled();
  });

  it('T66.9 should geoJSON layer to cluster group for a given cluster group', () => {
    let addSpy = spyOn(service, 'addGeoLayerToCluster').and.callThrough();
    service.addGeoLayerToCluster([], new L.MarkerClusterGroup);
    expect(addSpy).toHaveBeenCalled();
  });

});
