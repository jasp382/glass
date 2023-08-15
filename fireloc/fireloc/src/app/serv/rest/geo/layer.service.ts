import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { api } from 'src/apicons';

/**
 * Service for making API requests related to FireLoc geospatial layers.
 */
@Injectable({
  providedIn: 'root'
})
export class LayerService {

  /**
   * Empty constructor
   * @param http Http client used to make the API calls
   */
  constructor(private http: HttpClient) { }

  /**
   * Requests API to get a list of all geospatial layers for non-authenticated users.
   * @returns API request made
   */
  getLayersNoToken() {
    const httpOptions = { headers: new HttpHeaders({ 'Content-Type': 'application/json' }) };
    return this.http.get(api.layersUrl, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to get a list of all geospatial layers for authenticated users.
   * @param asTree optional filter to return results in a tree structure
   * @returns API request made
   */
  getLayersToken(asTree?: boolean) {
    // HTTP Headers
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    // define get parameter
    let option = '?astree='
    if (asTree !== undefined) option += asTree; else option = '';

    let url = api.layersTokenUrl + option;
    return this.http.get(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to create a new geospatial layer.
   * @param data geospatial layer information
   * @returns API request made
   */
  createLayer(data: any) {
    // HTTP Headers
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.post(api.layersTokenUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to update a geospatial layer.
   * @param slug layer slug to use as ID
   * @param data geospatial layer information
   * @returns API request made
   */
  updateLayer(slug: string, data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.layerUrl + slug + '/';
    return this.http.put(url, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to delete a geospatial layer.
   * @param slug layer slug to use as ID
   * @returns API request made
   */
  deleteLayer(slug: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.layerUrl + slug + '/';
    return this.http.delete(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }


  /* ----- Group-Layer Association ----- */

  /**
   * Requests API update geospatial layers visible to users of a group.
   * @param groupName user group name to update layers visibility
   * @param layersSlugs array of geospatial layer slugs to use as IDs
   * @param type can be 'delete' to delete layers or 'add' to add layers
   * @returns API request made
   */
  setGroupLayers(groupName: string, layersSlugs: string[], type: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    let data = {};
    if (type === 'delete') data = { 'layers_del': layersSlugs };
    else data = { 'layers_add': layersSlugs }; // type === 'add'

    let url = api.groupLayersUrl + groupName + '/';
    return this.http.put(url, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API delete all geospatial layers visible to users of a group.
   * @param groupName user group name to update layers visibility
   * @returns API request made
   */
  deleteGroupLayers(groupName: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.groupLayersUrl + groupName + '/';
    return this.http.delete(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

}