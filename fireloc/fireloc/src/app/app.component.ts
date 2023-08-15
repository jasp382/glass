import { Component, HostListener, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { NgbAlert, NgbAlertConfig } from '@ng-bootstrap/ng-bootstrap';
import { Observable } from 'rxjs';

// Redux
import { select } from '@angular-redux/store';
import { AlertActions } from './redux/actions/alertActions';
import { LangActions } from './redux/actions/langActions';
import { selectAlertMessage, selectHasAlert, selectLanguage } from './redux/selectors';

// Services
import { AuthService } from './serv/rest/users/auth.service';
import { TranslateService } from '@ngx-translate/core';

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
export class AppComponent implements OnInit, OnDestroy {

  /**
   * app title
   */
  title = 'fireloc';

  /**
   * Redux selector for alert message state
   */
  @select(selectAlertMessage) alertMessage$!: Observable<any>;
  /**
   * Redux selector for has alert state
   */
  @select(selectHasAlert) hasAlert$!: Observable<boolean>;
  /**
   * Redux selector for language state
   */
  @select(selectLanguage) language$!: Observable<boolean>;

  // app alert
  /**
   * alert message content
   */
  alertMessage: string = '';
  /**
   * alert message type
   */
  alertType: string = '';
  /**
   * flag to determine if there is an alert to display
   */
  hasAlert: boolean = false;
  /**
   * reference for Bootstrap alert
   */
  @ViewChild('selfClosingAlert', { static: false }) appAlert!: NgbAlert;

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
    private authServ: AuthService,
    alertConfig: NgbAlertConfig,
    private alertActions: AlertActions,
    private langActions: LangActions,
    public translate: TranslateService
  ) {
    // customize component default alerts
    alertConfig.dismissible = true;

    // multi-language support
    translate.addLangs(['pt', 'en']);
    translate.setDefaultLang('pt');
  }

  /**
   * Checks whether the language has been saved in storage and subscribes to Redux updates.
   */
  ngOnInit(): void {
    let savedLanguage = localStorage.getItem('lang');

    this.subscribeToRedux();

    // keep selected language
    if (savedLanguage !== null) this.langActions.changeLanguage(savedLanguage);
  }

  /**
   * Logs out user if session is not meant to be kept when user closes browser window/tab
   */
  @HostListener('window:beforeunload')
  ngOnDestroy(): void {
    let rememberUser = this.authServ.getRememberUser();
    let isLoggedIn = this.authServ.isLoggedIn();
    // if user did not keep the session, log out
    if (isLoggedIn && !rememberUser) this.authServ.logout();
  }

  /**
   * Subscribes to Redux to receive updates about alerts and app language changes.
   */
  subscribeToRedux() {
    // update the alert message value
    this.alertMessage$.subscribe(
      (alertMessage: any) => {
        this.alertMessage = alertMessage.message;
        this.alertType = alertMessage.type;
        // if alert type is empty, apply the default
        if (this.alertType === '') this.alertType = 'warning';

      }
    );

    // update the hasAlert variable
    this.hasAlert$.subscribe(
      (hasAlert: boolean) => {
        this.hasAlert = hasAlert;
        // if it's meant to show an alert, show it
        if (hasAlert === true) this.showAlert();
      }
    );

    // update the language used in the app
    this.language$.subscribe(
      (language: any) => {
        this.switchLang(language);
        localStorage.setItem('lang', language);
      }
    );
  }

  /**
   * Displays the Bootstrap alert and automatically closes it after 5 seconds. 
   * User can also manually close it anytime before that.
   */
  showAlert() {
    setTimeout(() => {
      // close the alert after 5 seconds
      this.appAlert.close();
      this.alertActions.resetAlert();
    }, 5000);
  }

  /**
   * Switches the language used in the application
   * @param lang new language to use
   */
  switchLang(lang: string) { this.translate.use(lang); }

}
