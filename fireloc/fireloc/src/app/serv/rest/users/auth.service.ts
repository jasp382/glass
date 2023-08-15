import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from "@angular/router";
import { map } from 'rxjs/operators';
import { api } from 'src/apicons';

// Redux
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';

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
  constructor(
    private http: HttpClient,
    private router: Router,
    private contribActions: ContributionActions,
    private eventActions: EventActions
  ) { if (this.isLoggedIn()) this.setRememberUser(true); }

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
    return this.http.post(api.tokenurl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
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
   * Requests the API to send a password recovery email.
   * @param email email of the user wanting to recover the account password
   * @returns API request made
   */
  resetPassword(email: string) {
    let data = { 'email': email };
    return this.http.put(api.recoverpswUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests the API to change a user account's password.
   * @param token token sent by email to the user
   * @param newPassword new password to update user's credentials
   * @returns API request made
   */
  changePassword(token: string, newPassword: string) {
    let data = { 'token': token, 'password': newPassword };
    return this.http.put(api.changepswUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests the API to register a new user. See {@link SignupComponent} for usage example.
   * @param name new user's first name
   * @param lastName new user's surnames
   * @param email new user's email
   * @param password new user's password
   * @returns API request made
   */
  registerUser(name: string, lastName: string, email: string, password: string) {
    let data = { 'email': email, 'password': password, 'first_name': name, 'last_name': lastName };
    return this.http.post(api.justuserUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Requests the API to send a registration confirmation to the user's email.
   * @param email user email to be used as ID
   * @returns API request made
   */
  sendRegistrationConfirmation(email: string) {
    let data = { 'email': email };
    return this.http.put(api.regconfirmationUrl, data, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
  }

  /**
   * Checks whether a user is currently logged in or not
   * @returns true if user is logged in, false if otherwise
   */
  isLoggedIn() {
    let access_token = localStorage.getItem('access_token');
    let refresh_token = localStorage.getItem('refresh_token');
    let type_token = localStorage.getItem('type_token');
    let expiration = localStorage.getItem('expiration');
    let userId = localStorage.getItem('userId');
    let login_time = localStorage.getItem('login_time');
    let user_role = localStorage.getItem('user_role');

    if (access_token && refresh_token && type_token && expiration && userId && login_time && user_role) {
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
  logout() {
    // remove info from local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('type_token');
    localStorage.removeItem('expiration');
    localStorage.removeItem('userId');
    localStorage.removeItem('login_time');
    localStorage.removeItem('user_role');
    localStorage.removeItem('userContributions');

    // remove contribution info from redux
    this.contribActions.removeAllContributions();
    this.contribActions.removeUserContributions();

    // remove event info from redux
    this.eventActions.clearEventLayers();
    this.eventActions.clearEvents();

    // redirect to homepage
    this.router.navigate(['/']);
  };
}
