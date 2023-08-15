import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { Language } from '../interfaces/language';

@Injectable({
  providedIn: 'root'
})
export class LangService {

  constructor() { }

  getLanguage(lang: Language): Observable<Language> {

    let a: Language = {
      language: lang.language,
      country : lang.country
    };

    //return a;

    return of(a);
  };
}
