import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map } from 'rxjs/operators';
import { api } from 'src/apicons';

/**
 * Service for making API requests related to FireLoc user groups.
 */
@Injectable({
  providedIn: 'root'
})
export class GroupService {

  /**
   * Empty constructor. 
   * @param http Http client used to make the API calls
   */
  constructor(private http: HttpClient) { }

  /**
   * Requests the API to get a list of user groups in the FireLoc system. 
   * @param getUsers flag to get users in the request response
   * @param getLayers flag to get layers in the request response
   * @returns API request made
   */
  getGroups(getUsers: boolean, getLayers: boolean) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    let url = api.groupsUrl + '?users=' + getUsers + '&layers=' + getLayers;
    return this.http.get(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to add a new user group
   * @param groupName name of the new user group
   * @returns API request made
   */
  addGroup(groupName: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    let data = { "group": groupName };
    return this.http.post(api.groupsUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to update a user group
   * @param oldName old group name to be used as a group ID
   * @param newName new group name
   * @returns API request made
   */
  updateGroup(oldName: string, newName: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    let data = { "name": newName };
    let url = api.groupUrl + oldName + '/';
    return this.http.put(url, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to delete a user group
   * @param name group name to be used as a group ID
   * @returns API request made
   */
  deleteGroup(name: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    let url = api.groupUrl + name + '/';
    return this.http.delete(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }
}
