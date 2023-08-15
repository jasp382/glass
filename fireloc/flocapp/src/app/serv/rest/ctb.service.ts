import { Injectable } from '@angular/core';

import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { api } from '../../apicons';

import { Token } from '../../interfaces/login';
import { ContribApi, ContribByDayApi, ContribPhoto } from 'src/app/interfaces/contribs';

@Injectable({
  providedIn: 'root'
})
export class CtbService {

  constructor(private http: HttpClient) { }

  /**
	 * Request API to get a list of all contributions in the FireLoc system.
	 * @param userID optional filter to get one user's contributions
	 * @param startDate optional start date filter
	 * @param endDate optional end date filter
	 * @param fgeom optional geographical location filter
	 * @returns API request made
	 */
	getContributions(token: Token, strips?: number, userID?: (string | null), startDate?: string, endDate?: string, fgeom?: string) {
		// HTTP Headers
		const httpOptions = {
			headers: new HttpHeaders({
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + token.access_token
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
		let STRIPS = strips ? `&strips=${strips}` : '';
		let GEOMCTYPE = '&geomctype=coords';
		let LAYERS = '&layers=true';

		let parameters = '?epsg=' + EPSG + '&geom=' + GEOM
			+ '&usergeom=' + USERGEOM + '&geombf=' + GEOMBF
			+ USERID + STARTTIME + ENDTIME + FGEOM
			+ FEPSG + STRIPS + GEOMCTYPE + LAYERS;

		// define final request url with parameters
		let url = api.contribsUrl + parameters;
		return this.http.get<ContribApi>(url, httpOptions);
	};

	getContribByDay(token: Token, userID?: (string | null), startDate?: string, endDate?: string, fgeom?: string) {
		// HTTP Headers
		const httpOptions = {
			headers: new HttpHeaders({
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + token.access_token
			})
		};

		// define paramenters
		let GEOM = 'true';
		let USERGEOM = 'true';
		let GEOMBF = 'true';
		let EPSG = 4326;
		/* let EPSG = 4326; */

		// define url parameters
		let USERID = userID ? `&userid=${userID}` : '';
		let STARTTIME = startDate ? `&starttime=${startDate}` : '';
		let ENDTIME = endDate ? `&endtime=${endDate}` : '';
		let FGEOM = fgeom ? `&fgeom=${fgeom}` : '';
		let FEPSG = fgeom ? '&fepsg=4326' : '';
		let GEOMCTYPE = '&geomctype=coords';
		let GEOMC = '&geomc=true';
		let LAYERS = '&layers=true';

		let parameters = '?orient=date&strips=6&epsg=' + EPSG + '&geom=' + GEOM + '&usergeom=' + USERGEOM + '&geombf=' + GEOMBF
			+ USERID + STARTTIME + ENDTIME + FGEOM 
			+ FEPSG + GEOMC + GEOMCTYPE + LAYERS;

		// define final request url with parameters
		let url = api.contribsUrl + parameters;
		return this.http.get<ContribByDayApi>(url, httpOptions);
	};

	/**
	 * Request API to get a photo associated to a contribution.
	 * @param photoName contribution photo name
	 * @returns API request made
	 */
	getContributionPhoto(token: Token, photoName: string) {
		// HTTP Headers
		const httpOptions = {
			headers: new HttpHeaders({
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + token.access_token
			})
		};

		let url = api.url + photoName;

		return this.http.get<ContribPhoto>(url, httpOptions);
	}
}
