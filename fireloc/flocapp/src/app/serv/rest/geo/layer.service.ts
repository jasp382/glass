import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

// constants and interfaces
import { api } from 'src/app/apicons';
import { TreeLayerApi } from 'src/app/interfaces/layers';
import { Token } from 'src/app/interfaces/general';



@Injectable({
  providedIn: 'root'
})
export class LayerService {

  /**
   * Constructor
   * @param http Http client used to make the API calls
   */
  constructor(
    private http: HttpClient
  ) { }

  /**
   * Requests API to get a list of all geospatial layers.
   * @returns API request made
   */
  getLayers(token: Token|null, asTree?:boolean) {

    // define get parameter
    let option = '?astree='
    if (asTree !== undefined) option += asTree; else option = '';

    let burl = token !== null ? api.layersTokenUrl : api.layersUrl;
    let url = burl + option;
    
    if (token === null) {
      const httpOptions = { headers: new HttpHeaders({
        'Content-Type': 'application/json'
      }) };

      return this.http.get<TreeLayerApi>(url, httpOptions);
    } else {
      const httpOptions = { headers: new HttpHeaders({
        'Content-Type'  : 'application/json',
        'Authorization' : 'Bearer ' + token.access_token
      }) };

      return this.http.get<TreeLayerApi>(url, httpOptions);
    }
  }
}
