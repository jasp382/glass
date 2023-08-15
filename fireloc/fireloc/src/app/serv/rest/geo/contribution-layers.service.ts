import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map } from 'rxjs/operators';
import { api } from 'src/apicons';

/**
 * Service for making API requests related to contribution geospatial layers.
 */
@Injectable({
  providedIn: 'root'
})
export class ContributionLayersService {

  /**
   * Empty constructor
   * @param http Http client used to make the API calls
   */
  constructor(private http: HttpClient) { }

  /**
   * Requests the API to get a list of contribution geospatial layers in the FireLoc system. 
   * @returns API request made
   */
  getContribLayers() {
    // HTTP Headers
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    let url = api.contribLayersUrl;
    return this.http.get(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests the API to get a web feature service. 
   * See [Main Component]{@link MainfrontComponent#getContribLayer} for usage example.
   * @param workspace web feature service workspace name
   * @param layerName web feature service layer name
   * @param boudingBox map bounds for viewable content
   * @returns 
   */
  getWebFeatureService(workspace: string, layerName: string, boudingBox?: string) {
    // HTTP Headers
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    let filter = '';
    if(boudingBox) {
      filter = `?epsg=4326&?bbox=${boudingBox}&bboxsrs=4326`;
    }

    let url = api.geoMapServicesUrl + `${workspace}/${layerName}/${filter}`;
    return this.http.get(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

}
