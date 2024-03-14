import { Injectable } from '@angular/core';

import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Geometry } from '../interfaces';

@Injectable({
  providedIn: 'root'
})
export class GeosService {

  constructor(private http: HttpClient) { }

  getGeoms(layerid:number) {
    return this.http.get<Geometry[]>('http://localhost:8000/geoms/' + String(layerid) + '/');
  };

  delGeoms(layerid:number) {
    let headers = new HttpHeaders();

    headers = headers.set(
        'Content-Type',
        'application/json; charset=utf-8'
    );

    return this.http.delete(
      'http://localhost:8000/geoms/' + String(layerid) + '/',
      {headers : headers}
    );
  }
}
