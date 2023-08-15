import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { api } from 'src/app/apicons';

import { Token } from 'src/app/interfaces/login';
import { NewUser, User } from 'src/app/interfaces/users';
import { Observable, of } from 'rxjs';

/**
 * Http headers to be used in API request calls.
 */
const httpOptions = { headers: new HttpHeaders({ 'Content-Type': 'application/json' }) };


/**
 * Service for making API requests related to FireLoc authentication and checking authentication status.
 */
@Injectable({
  providedIn: 'root'
})
export class AuthService {

  /**
   * Flag to keep or logout user session after browser close
   */
  rememberUser: boolean = false;


  /**
   * Authentication Service constructor. Sets the user session status according to logged status.
   * @param http Http client used to make the API calls
   * @param router router used for navigation within the app
   * @param contribActions Redux contribution actions 
   * @param eventActions Redux event actions
   */
  constructor(private http: HttpClient) { }

  /**
   * Gets user's keep session value.
   * @returns user's keep session value.
   */
  getRememberUser() {
    return this.rememberUser;
  }

  /**
   * Sets user's keep session value.
   * @param remember user's keep session value.
   */
  setRememberUser(remember: boolean) {
    this.rememberUser = remember;
  }

  /**
   * Requests API to authenticate a user with given credentials.
   * @param email user email
   * @param password user password
   * @returns API request made
   */
  login(email: string, password: string) {
    let data = { 'userid': email, 'password': password };

    return this.http.post<Token>(
      api.tokenurl, data, httpOptions
    );
  };

  updateToken(token: Token): Observable<Token> {
    return of(token);
  };

  updateUserID(userid: string): Observable<string> {
    return of(userid);
  };

  /**
   * Refreshes the user authentication token.
   * @returns API request made
   */
  refreshToken() {
    let data = { 'token': localStorage.getItem('refresh_token') };

    return this.http.post(api.renewurl, data, httpOptions).pipe(map(response => {
      let result = JSON.parse(JSON.stringify(response));

      let access_token: string = result.access_token,
        refresh_token: string = result.refresh_token,
        expiration: string = result.expires_in,
        date: any = Date.now();

      if (result && access_token && refresh_token && expiration && date) {
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('expiration', expiration);
        localStorage.setItem('login_time', date.toString());
      }
    }));
  };

  /**
   * Checks whether a user is currently logged in or not
   * @returns true if user is logged in, false if otherwise
   */
  isLoggedIn() {
    let access_token = localStorage.getItem('access_token');
    let refresh_token = localStorage.getItem('refresh_token');
    let type_token = localStorage.getItem('type_token');
    let expiration = localStorage.getItem('expiration');
    //let userId = localStorage.getItem('userId');
    let login_time = localStorage.getItem('login_time');
    let user_role = localStorage.getItem('user_role');

    if (access_token && refresh_token && type_token && expiration && login_time && user_role) {
      let isExpired: boolean = this.isTokenExpired(expiration, login_time);
      if (isExpired && refresh_token) {
        this.refreshToken();
        isExpired = this.isTokenExpired(expiration, login_time);
      }
      if (!isExpired) return true;
      else {
        this.logout();
        return false;
      }
    }
    else return false;
  };

  /**
   * Checks whether the user's authentication token has expired
   * @param expiration token expiration
   * @param login_time time of user login
   * @returns true if authentication token is expired, false if otherwise
   */
  isTokenExpired(expiration: string, login_time: string) {
    let current_time = Date.now();
    let isExpired = false;
    if (expiration && login_time && current_time && Number(current_time) - Number(login_time) > Number(expiration) * 1000) {
      isExpired = true;
    }
    return isExpired;
  };

  /**
   * Terminates a user's session. 
   * Removes all information from browser's local storage and redirects the user to the app's homepage.
   */
  logout(): Observable<boolean> {
    // remove info from local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('type_token');
    localStorage.removeItem('expiration');
    localStorage.removeItem('userId');
    localStorage.removeItem('login_time');
    localStorage.removeItem('user_role');

    // redirect to homepage
    //this.router.navigate(['/']);

    return of(true);
  }

  /**
   * Requests the API to register a new user. See {@link SignupComponent} for usage example.
   * @param name new user's first name
   * @param lastName new user's surnames
   * @param email new user's email
   * @param password new user's password
   * @returns API request made
   */
  registerUser(newUser: NewUser) {
    let data = {
      'email': newUser.email, 'password': newUser.password,
      'first_name': newUser.name, 'last_name': newUser.lastName
    };

    return this.http.post<User>(api.justuserUrl, data, httpOptions);
  }
}
