import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { api } from '../../../apicons';

/**
 * Service for making API requests related to FireLoc contributions.
 */
@Injectable({
	providedIn: 'root'
})
export class ContribService {

	/**
	 * Empty constructor
	 * @param http Http client used to make the API calls
	 */
	constructor(private http: HttpClient) { }

	/**
	 * Request API to get a list of all contributions in the FireLoc system.
	 * @param userID optional filter to get one user's contributions
	 * @param startDate optional start date filter
	 * @param endDate optional end date filter
	 * @param fgeom optional geographical location filter
	 * @returns API request made
	 */
	getContributions(userID?: (string | null), startDate?: string, endDate?: string, fgeom?: string) {
		// HTTP Headers
		const httpOptions = {
			headers: new HttpHeaders({
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + localStorage.getItem('access_token')
			})
		};

		// define paramenters
		let GEOM = 'true';
		let USERGEOM = 'true';
		let GEOMBF = 'true';
		let EPSG = 3763;
		/* let EPSG = 4326; */

		// define url parameters
		let USERID = userID ? `&userid=${userID}` : '';
		let STARTTIME = startDate ? `&starttime=${startDate}` : '';
		let ENDTIME = endDate ? `&endtime=${endDate}` : '';
		let FGEOM = fgeom ? `&fgeom=${fgeom}` : '';
		let FEPSG = fgeom ? '&fepsg=4326' : '';

		let parameters = '?epsg=' + EPSG + '&geom=' + GEOM + '&usergeom=' + USERGEOM + '&geombf=' + GEOMBF
			+ USERID + STARTTIME + ENDTIME + FGEOM + FEPSG;

		// define final request url with parameters
		let url = api.contribsUrl + parameters;
		return this.http.get(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
	};

	/**
	 * Request API to get a photo associated to a contribution.
	 * @param photoName contribution photo name
	 * @returns API request made
	 */
	getContributionPhoto(photoName: string) {
		// HTTP Headers
		const httpOptions = {
			headers: new HttpHeaders({
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + localStorage.getItem('access_token')
			})
		};

		let url = api.url + photoName;
		return this.http.get(url, httpOptions).pipe(map(r => JSON.parse(JSON.stringify(r))));
	}

}