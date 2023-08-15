import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map } from 'rxjs/operators';
import { api } from 'src/apicons';

/**
 * Service for making API requests related to FireLoc raster datasets.
 */
@Injectable({
  providedIn: 'root'
})
export class RasterService {

  /**
   * Empty constructor
   * @param http Http client used to make the API calls
   */
  constructor(private http: HttpClient) { }

  /**
   * Requests API to get a list of all raster datasets in the FireLoc system.
   * @returns API request made
   */
  getRasterDatasets() {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.get(api.rasterDatasetsUrl, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  };

  /**
   * Requests API to create a new raster dataset.
   * @param data raster dataset information
   * @returns API request made
   */
  addRasterDataset(data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.post(api.rasterDatasetsUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  };

  /**
   * Requests API to update a raster dataset.
   * @param rasterSlug raster dataset slug to use as ID
   * @param data raster dataset information
   * @returns API request made
   */
  updateRasterDataset(rasterSlug: string, data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.rasterDatasetUrl + rasterSlug + '/';
    return this.http.put(url, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to delete a raster dataset.
   * @param rasterSlug raster dataset slug to use as ID
   * @returns API request made
   */
  deleteRasterDataset(rasterSlug: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.rasterDatasetUrl + rasterSlug + '/';
    return this.http.delete(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to get a list of all raster dataset types in the FireLoc system.
   * @returns API request made
   */
  getRasterTypes() {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.get(api.rasterTypesUrl, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }
}
