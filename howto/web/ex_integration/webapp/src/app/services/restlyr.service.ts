import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Layers, GeoserverLayerResponse, StyleData } from '../interfaces';

@Injectable({
  providedIn: 'root'
})
export class RestlyrService {

    constructor(private http: HttpClient) { }

    getLayers() {
        return this.http.get<Layers[]>('http://localhost:8000/layers/');
    }

    getLayer(id:number) {
        return this.http.get<Layers>('http://localhost:8000/layer/' + id);
    }

    addLayer(lyr: Layers) {
        let headers = new HttpHeaders();

        headers = headers.set(
            'Content-Type',
            'application/json; charset=utf-8'
        );
        return this.http.post<Layers>(
            'http://localhost:8000/layers/',
            JSON.stringify(lyr),
            {headers : headers}
        );
    }

    updateLayer(lyr: Layers) {
        let headers = new HttpHeaders();

        headers = headers.set(
            'Content-Type',
            'application/json; charset=utf-8'
        );
        return this.http.put<Layers>(
            'http://localhost:8000/layer/' + lyr.id + '/',
            JSON.stringify(lyr),
            {headers : headers}
        );
    }

    delLayer(id: number) {
        let headers = new HttpHeaders();

        headers = headers.set(
            'Content-Type',
            'application/json; charset=utf-8'
        );
        return this.http.delete(
            'http://localhost:8000/layer/' + id + '/',
            {headers : headers}
        )
    };

    addGeoServerLayer(id:number) {
        let headers = new HttpHeaders();

        headers = headers.set(
            'Content-Type',
            'application/json; charset=utf-8'
        );

        return this.http.post<GeoserverLayerResponse>(
            'http://localhost:8000/geoserver/addlayer/' + id + '/',
            {headers : headers}
        )
    }

    addGeoServerStyle(id: number, data: StyleData) {
        let headers = new HttpHeaders();

        headers = headers.set(
            'Content-Type',
            'application/json; charset=utf-8'
        );

        return this.http.post(
            'http://localhost:8000/geoserver/style/' + id + '/',
            JSON.stringify(data),
            {headers : headers}
        )
    }
    
}
