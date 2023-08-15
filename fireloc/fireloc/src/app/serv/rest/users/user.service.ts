import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { api } from 'src/apicons';

/**
 * Service for making API requests related to FireLoc users.
 */
@Injectable({
  providedIn: 'root'
})
export class UserService {

  /**
   * Empty constructor. 
   * @param http Http client used to make the API calls
   */
  constructor(private http: HttpClient) { }

  /**
   * Requests API to get information related to the logged user.
   * @returns API request made
   */
  getUser() {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    let userID = localStorage.getItem('userId');
    let url = api.userUrl + userID + '/';
    return this.http.get(url, httpOptions);
  };

  /**
   * Requests API to add a new FireLoc or Risk Manager user.
   * @param user new user information
   * @returns API request made
   */
  addAdminUser(user: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    return this.http.post(api.usersUrl, user, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests API to add a new user without privileges.
   * @param user new user information
   * @returns API request made
   */
  addUser(user: any) {
    const httpOptions = { headers: new HttpHeaders({ 'Content-Type': 'application/json', }) };
    return this.http.post(api.justuserUrl, user, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))))
  }

  /**
   * Requests the API to updates a user's information.
   * @param email email used as ID to identify the desired user to update
   * @param userData new user information
   * @returns API request made
   */
  updateUser(email: string, userData: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    let url = api.userUrl + email + '/';
    return this.http.put(url, userData, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests the API to delete a user.
   * @param email email used as ID to identify the desired user to delete
   * @returns API request made
   */
  deleteUser(email: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    let url = api.userUrl + email + '/';
    return this.http.delete(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests the API to get a list of users in the FireLoc system.
   * @param groups optional list to filter results by user group
   * @returns API request made
   */
  getUsers(groups?: string[]) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };
    let groupFilter = '';

    // if there are groups, filter by group
    if (groups && groups.length !== 0) {
      groupFilter = '?groups=';
      // add groups to filter
      groups.forEach((g, index) => {
        if (index === 0) groupFilter += g;
        else groupFilter += `,${g}`;
      })
    }

    let url = api.usersUrl + groupFilter;
    return this.http.get(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests the API to get a list of user attributes.
   * @returns API request made
   */
  getUserAttributes() {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
      })
    };

    return this.http.get(api.attrsUrl, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

}
