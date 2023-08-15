import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { map } from 'rxjs/operators';
import { api } from 'src/app/apicons';
import { Token } from 'src/app/interfaces/general';
import { UserApi, User } from 'src/app/interfaces/users';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http: HttpClient) { }

  /**
   * Requests the API to get a list of users in the FireLoc system.
   * @param groups optional list to filter results by user group
   * @returns API request made
   */
  getUsers(token: Token, groups?: string[]) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token.access_token
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
    return this.http.get<UserApi>(url, httpOptions);
  }

  /**
   * Requests API to get information related to the logged user.
   * @returns API request made
   */
  getUser(token: Token, userid: string) {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token.access_token
      })
    };

    let url = api.userUrl + userid + '/';

    return this.http.get<User>(url, httpOptions);
  }
}
