import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map } from 'rxjs/operators';
import { api } from 'src/apicons';

/**
 * Service for making API requests related to FireLoc satellite datasets.
 */
@Injectable({
  providedIn: 'root'
})
export class SatelliteService {

  /**
   * Empty constructor
   * @param http Http client used to make the API calls
   */
  constructor(private http: HttpClient) { }

  /**
   * Requests API to get a list of all satellite datasets in the FireLoc system.
   * @returns API request made
   */
  getSatDatasets() {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.get(api.satDatasetsUrl, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  };

  /**
   * Requests API to delete a satellite dataset.
   * @param id satellite dataset ID
   * @returns API request made
   */
  deleteSatDataset(id: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.satDatasetUrl + id + '/';
    return this.http.delete(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }
}
