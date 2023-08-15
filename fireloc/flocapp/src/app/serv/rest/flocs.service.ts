import { Injectable } from '@angular/core';

import { HttpClient, HttpHeaders } from '@angular/common/http';
import { api } from '../../apicons';

import { Token } from 'src/app/interfaces/login';
import { FirelocApi } from 'src/app/interfaces/fireloc';

@Injectable({
  providedIn: 'root'
})
export class FlocsService {

	constructor(private http: HttpClient) { }

  getFirelocs(token: Token|null, step?:string) {
    let _step = !step ? '' : `&step=${step}`;
	  let qp = '?contribs=true&geom=false&extent=false&countcontribs=true' + _step;
    if (token === null) {
      const httpOptions = { headers: new HttpHeaders({
        'Content-Type': 'application/json'
      }) };
      return this.http.get<FirelocApi>(
		api.firelocUrl + qp,
		httpOptions
	);
    } else {
      const httpOptions = { headers: new HttpHeaders({
        'Content-Type'  : 'application/json',
        'Authorization' : 'Bearer ' + token.access_token
      }) };

      return this.http.get<FirelocApi>(
		    api.firelocTokenUrl + qp,
		    httpOptions
	    );
    }
  }
}
