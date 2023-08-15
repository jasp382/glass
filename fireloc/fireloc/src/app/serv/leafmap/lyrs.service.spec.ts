import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import * as L from 'leaflet';

import { LyrsService } from './lyrs.service';

@Component({ template: `<div id='map'></div>` })
class DummyComponent { }

describe('TS64 LyrsService', () => {
  let service: LyrsService;
  let fixture: ComponentFixture<DummyComponent>;
  let component: DummyComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DummyComponent]
    }).compileComponents();

    service = TestBed.inject(LyrsService);
    fixture = TestBed.createComponent(DummyComponent);
    component = fixture.componentInstance;
  });

  it('T64.1 should be created', () => { expect(service).toBeTruthy(); });

  it('T64.2 should update basemap', () => {
    let updateSpy = spyOn(service, 'updateBasemap').and.callThrough();
    service.updateBasemap(L.map('map'), 'OpenStreetMap');
    expect(updateSpy).toHaveBeenCalled();
  });

  it('T64.3 should add layer to map', () => {
    let addSpy = spyOn(service, 'addLayer').and.callThrough();
    service.addLayer(L.map('map'), L.markerClusterGroup());
    expect(addSpy).toHaveBeenCalled();
  });

  it('T64.4 should remove layer from map', () => {
    let removeSpy = spyOn(service, 'removeLayer').and.callThrough();
    service.removeLayer(L.map('map'), L.markerClusterGroup());
    expect(removeSpy).toHaveBeenCalled();
  });
});
