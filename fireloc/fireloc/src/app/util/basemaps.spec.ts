import * as L from "leaflet";
import { Basemaps } from "./basemaps";

describe('TS80 Basemaps Functions', () => {
  var basemap: Basemaps;

  beforeEach(() => {
    basemap = new Basemaps();
  });

  it('T80.1 should return desired layer for map', () => {
    let getLayerSpy = spyOn(basemap, 'getLayer').and.callThrough();

    // open street map
    let resultOpen = basemap.getLayer(Basemaps.servicesList[0]);
    expect(resultOpen).toEqual(L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }));

    // ESRI Streets
    let resultESRI = basemap.getLayer(Basemaps.servicesList[1]);
    expect(resultESRI).toEqual(L.tileLayer('http://services.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19, attribution: '&copy; @ESRI'
    }));

    // Satellite
    let resultSatellite = basemap.getLayer(Basemaps.servicesList[2]);
    expect(resultSatellite).toEqual(L.tileLayer(
      'https://api.mapbox.com/v4/{id}/{z}/{x}/{y}@2x.jpg90?access_token=pk.eyJ1IjoiamFzcDEyIiwiYSI6ImNqNnRwYnF3MDA0YXkycXM0M210M3FtejQifQ.KfkaOt8Xc02oPI9lBUtHrA',
      { maxZoom: 19, attribution: 'Basemap from @ <a href="https://www.mapbox.com/">Mapbox</a>', tileSize: 512, zoomOffset: -1, id: 'mapbox.satellite' }
    ));

    // Default
    let resultDefault = basemap.getLayer('');
    expect(resultDefault).toEqual(L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }));

    expect(getLayerSpy).toHaveBeenCalledTimes(4);
  });

});