import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { api } from 'src/app/apicons';

import { Token } from 'src/app/interfaces/general';
import { ClusterLayer, ClusterLyrAPI, GeoJSONAPI } from 'src/app/interfaces/layers';

/**
 * Service for making API requests related to geoserver geospatial layers.
 */
@Injectable({
  providedIn: 'root'
})
export class GeosrvService {

  constructor(private http: HttpClient) { }

  clusterLayerIsActive (lyr: ClusterLayer): Observable<ClusterLayer> {
    return of(lyr);
  }

  mainLayerActiveStatus (isActive: boolean): Observable<boolean> {
    return of(isActive);
  }

  /**
   * Requests the API to get a list of contribution geospatial layers in the FireLoc system. 
   * @returns API request made
   */
  getClusterLayers(token: Token) {
    // HTTP Headers
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token.access_token
      })
    };

    let url = api.clusterLayersUrl;

    return this.http.get<ClusterLyrAPI>(url, httpOptions);
  }

  /**
   * Requests the API to get a web feature service. 
   * See [Main Component]{@link MainfrontComponent#getContribLayer} for usage example.
   * @param workspace web feature service workspace name
   * @param layerName web feature service layer name
   * @param boudingBox map bounds for viewable content
   * @returns 
   */
  getWFS(token: Token, workspace: string, layerName: string, boudingBox?: string) {
    // HTTP Headers
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': token.token_type + ' ' + token.access_token
      })
    };

    let filter = '';
    if(boudingBox) {
      filter = `?epsg=4326&?bbox=${boudingBox}&bboxsrs=4326`;
    }

    let url = api.geoMapServicesUrl + `${workspace}/${layerName}/${filter}`;
    
    return this.http.get<GeoJSONAPI>(url, httpOptions);
  }


}
