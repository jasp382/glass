import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { api } from '../../../apicons';

/**
 * Service for making API requests related to FireLoc fire events.
 */
@Injectable({
	providedIn: 'root'
})
export class EventService {

	/**
	 * Empty constructor
	 * @param http Http client used to make the API calls
	 */
	constructor(private http: HttpClient) { }

	/**
	 * Requests API to get a list of all fire events for non-authenticated users.
	 * @returns API request made
	 */
	getEventsNoToken() {
		// HTTP Headers
		const httpOptions = {
			headers: new HttpHeaders({ 'Content-Type': 'application/json', })
		};
		return this.http.get(api.eventUrl, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
	}

	/**
	 * Requests API to get a list of all fire events for authenticated users.
	 * @returns API request made
	 */
	getEventsToken() {
		// HTTP Headers
		const httpOptions = {
			headers: new HttpHeaders({
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + localStorage.getItem('access_token')
			})
		};
		return this.http.get(api.eventTokenUrl, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
	}

}