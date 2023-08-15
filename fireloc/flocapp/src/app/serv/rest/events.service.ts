import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { map } from 'rxjs/operators';
import { api } from '../../apicons';

import { Token } from 'src/app/interfaces/general';
import { FireEventApi } from 'src/app/interfaces/events';


/**
 * Service for making API requests related to real fire events.
 */

@Injectable({
  providedIn: 'root'
})
export class EventsService {

  constructor(private http: HttpClient) { }

  getFireEvents(token: Token|null, startDate: string|null, endDate: string|null) {
    // define parameters
    let EPSG = 3763;
    let GEOM = false;

    // define query params string
    let params = '?epsg=' + EPSG + '&geom=' + GEOM;
    let url = api.realEventsUrl + params;

    if (token === null) {
      const httpOptions = { headers: new HttpHeaders({
        'Content-Type': 'application/json'
      }) };
      return this.http.get<FireEventApi>(url, httpOptions);
    } else {
      const httpOptions = { headers: new HttpHeaders({
        'Content-Type'  : 'application/json',
        'Authorization' : 'Bearer ' + token.access_token
      }) };

      return this.http.get<FireEventApi>(url, httpOptions);
    }
  }

  /**
   * Requests API to get a list of all real fire events for non-authenticated users.
   * @param startDate optional start date filter
   * @param endDate optional end date filter
   * @param fgeom optional geographical location filter
   * @returns API request made
   */
  getRealEventsNoToken(startDate?: string, endDate?: string, fgeom?: string) {
    // HTTP Headers
    const httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json', })
    };

    // define paramenters
    let STARTTIME = startDate;
    let ENDTIME = endDate;
    let GEOM = 'false';
    let EPSG = 3763; // shows hectares correctly

    // define url parameters
    /* let STSTR = STARTTIME === null ? '' : '&starttime=' + STARTTIME;
    let ENDSTR = ENDTIME === null ? '' : '&endtime=' + ENDTIME; */

    /* TODO DELETE THIS AND USE CODE BEFORE WHEN DATE FILTERING IS WORKING */
    let STSTR = '';
    let ENDSTR = '';

    // define final request url with parameters
    let parameters = '?epsg=' + EPSG + '&geom=' + GEOM + STSTR + ENDSTR;
    let url = api.realEventsUrl + parameters;

    return this.http.get(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to get a list of all real fire events for authenticated users.
   * @param startDate optional start date filter
   * @param endDate optional end date filter
   * @param fgeom optional geographical location filter
   * @returns API request made
   */
  getRealEventsToken(startDate?: string, endDate?: string, fgeom?: string) {
    // HTTP Headers
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    // define paramenters
    let GEOM = 'false';
    //let EPSG = 4326; // shows burned area in map correctly
    let EPSG = 3763; // shows hectares correctly

    let STARTTIME = startDate ? `&starttime=${startDate}` : '';
    let ENDTIME = endDate ? `&endtime=${endDate}` : '';

    let FGEOM = fgeom ? `&fgeom=${fgeom}` : '';
    let FEPSG = fgeom ? '&fepsg=4326' : '';

    // define final request url with parameters
    let parameters = '?epsg=' + EPSG + '&geom=' + GEOM + STARTTIME + ENDTIME + FGEOM + FEPSG;
    let url = api.realEventsTokenUrl + parameters;

    return this.http.get(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Request API to create a new real fire event.
   * @param data real fire event information
   * @returns API request made
   */
  addRealEvent(data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    return this.http.post(api.realEventsTokenUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  };

  /**
   * Request API to update a real fire event.
   * @param eventID real fire event ID
   * @param data real fire event information
   * @returns API request made
   */
  updateRealEvent(eventID: number, data: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.realEventTokenUrl + eventID + '/';
    return this.http.put(url, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Request API to delete a real fire event.
   * @param eventID real fire event ID
   * @returns API request made
   */
  deleteRealEvent(eventID: number) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let url = api.realEventTokenUrl + eventID + '/';
    return this.http.delete(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }
}
