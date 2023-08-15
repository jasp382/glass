import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map } from 'rxjs/operators';
import { api } from '../../../apicons';

/**
 * Service for making API requests related to FireLoc charts.
 */
@Injectable({
  providedIn: 'root'
})
export class ChartService {

  /**
   * Empty constructor
   * @param http Http client used to make the API calls
   */
  constructor(private http: HttpClient) { }

  /**
   * Requests API to get a list of all charts in the FireLoc system.
   * @returns API request made
   */
  getCharts() {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.get(api.chartsUrl, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  };

  /**
   * Request API to create a new chart.
   * @param data chart information
   * @returns API request made
   */
  addChart(data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.post(api.chartsUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Request API to update a chart.
   * @param chartSlug chart slug to use as ID
   * @param data chart information
   * @returns API request made
   */
  updateChart(chartSlug: string, data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.chartUrl + chartSlug + '/';
    return this.http.put(url, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Request API to delete a chart.
   * @param chartSlug chart slug to use as ID
   * @returns API request made
   */
  deleteChart(chartSlug: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.chartUrl + chartSlug + '/';
    return this.http.delete(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }
}
