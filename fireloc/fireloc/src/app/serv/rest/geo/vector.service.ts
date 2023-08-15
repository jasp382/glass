import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map } from 'rxjs/operators';
import { api } from 'src/apicons';

/**
 * Service for making API requests related to FireLoc vectorial datasets.
 */
@Injectable({
  providedIn: 'root'
})
export class VectorService {

  /**
   * Empty constructor
   * @param http Http client used to make the API calls
   */
  constructor(private http: HttpClient) { }

  // ---------- DATASETS

  /**
   * Requests API to get a list of all vectorial datasets in the FireLoc system.
   * @returns API request made
   */
  getVectorDatasets() {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.get(api.vecDatasetsUrl, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  };

  /**
   * Requests API to create a new vectorial dataset.
   * @param data vectorial dataset information
   * @returns API request made
   */
  addVectorDataset(data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.post(api.vecDatasetsUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  };

  /**
   * Requests API to update a vectorial dataset.
   * @param vecSlug vectorial dataset slug to use as ID
   * @param data vectorial dataset information
   * @returns API request made
   */
  updateVectorDataset(vecSlug: string, data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.vecDatasetUrl + vecSlug + '/';
    return this.http.put(url, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to delete a vectorial dataset.
   * @param vecSlug vectorial dataset slug to use as ID
   * @returns API request made
   */
  deleteVectorDataset(vecSlug: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.vecDatasetUrl + vecSlug + '/';
    return this.http.delete(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  // ---------- CATEGORIES

  /**
   * Requests API to get a list of all vectorial dataset categories in the FireLoc system.
   * @returns API request made
   */
  getVectorCategories() {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.get(api.vecCategoriesUrl, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  // ---------- LEVELS

  /**
   * Requests API to create a new vectorial dataset level.
   * @param data vectorial dataset level information
   * @returns API request made
   */
  addVectorLevel(data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.post(api.vecLevelsUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  };

  /**
   * Requests API to update a vectorial dataset level.
   * @param levelSlug vectorial dataset level slug to use as ID
   * @param data vectorial dataset level information
   * @returns API request made
   */
  updateVectorLevel(levelSlug: string, data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.vecLevelUrl + levelSlug + '/';
    return this.http.put(url, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to delete a vectorial dataset level.
   * @param levelSlug vectorial dataset level slug to use as ID
   * @returns API request made
   */
  deleteVectorLevel(levelSlug: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.vecLevelUrl + levelSlug + '/';
    return this.http.delete(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

}
