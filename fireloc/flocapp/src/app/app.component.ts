import { Component } from '@angular/core';

import { Observable } from 'rxjs';

// Services
import { TranslateService } from '@ngx-translate/core';

// Interfaces
import { Language } from './interfaces/language';

// NGRX
import { AppState } from './stores/app-state';
import { Store } from '@ngrx/store';

import * as fromLangAction from './stores/lang/lang.actions';
import * as fromLangSelector from './stores/lang/lang.reducer';
import * as loginActions from './stores/login/login.actions';
import { Token } from './interfaces/general';

/**
 * App component.
 * Has control over the entire application's content.
 * 
 * Also features the success and error alerts for API responses.
 */
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  /**
   * app title
   */
  title = 'Fireloc Web Portal';

  language$: Observable<Language> = this.store.select(fromLangSelector.getLang);

  /**
   * Constructor for the app component.
   * Customizes the Bootstrap alerts and adds multi-language support to the application.
   * @param authServ authentication service. See {@link AuthService}.
   * @param alertConfig Bootstrap alert configuration
   * @param alertActions Redux alert actions. See {@link AlertActions}.
   * @param langActions Redux language actions. See {@link LangActions}.
   * @param translate translation service
   */
  constructor(
    private store: Store<AppState>,
    public translate: TranslateService
  ) {
    // multi-language support
    translate.addLangs(['pt', 'en']);
    translate.setDefaultLang('pt');
  }

  ngOnInit(): void {
    let savedLanguage = localStorage.getItem('lang');

    let lang: Language = {
      language: savedLanguage === 'pt' ? 'Português' : 'English',
      country: savedLanguage === 'pt' ? 'pt' : 'gb'
    }

    if (savedLanguage !== null) {
      this.store.dispatch(fromLangAction.GetLanguage({payload: lang}));
    };

    // update the language used in the app
    // when we have a change in the Language Store
    this.language$.subscribe(
      (language: Language) => {
        let _lang:string = language.country === 'pt' ? 'pt' : 'en';
        this.switchLang(_lang);
        localStorage.setItem('lang', _lang);
      }
    );

    let access_token = localStorage.getItem('access_token'),
        expires_in   = localStorage.getItem('expiration'),
        token_type   = localStorage.getItem('type_token'),
        scope        = localStorage.getItem('scope'),
        refresh_toke = localStorage.getItem('refresh_token'),
        role         = localStorage.getItem('user_role'),
        userid       = localStorage.getItem('userId');

    if (access_token !== null && expires_in !== null && 
      token_type !== null && scope !== null && 
      refresh_toke !== null && role !== null && userid !== null) {
      
      let _token: Token = {
        access_token  : access_token,
        expires_in    : Number(expires_in),
        token_type    : token_type,
        scope         : scope,
        refresh_token : refresh_toke,
        role          : role,
        status        : {code: '', message: ''}
      }
      
      this.store.dispatch(loginActions.UpdateToken({payload: _token}));

      this.store.dispatch(loginActions.UpdateUserID({payload: userid}));
    }
  };

  /**
   * Switches the language used in the application
   * @param lang new language to use
   */
  switchLang(lang: string) { this.translate.use(lang); }
}
