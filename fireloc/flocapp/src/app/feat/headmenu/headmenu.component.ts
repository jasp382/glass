import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { Router } from "@angular/router";

import { Observable } from 'rxjs';

// Interfaces and Constants
import { NavLink } from 'src/app/interfaces/navLink';
import { Language } from 'src/app/interfaces/language';
import { links } from '../../constants/navLinks';
import { languages } from '../../constants/languages';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as loginSelector from '../../stores/login/login.reducer';
import * as loginActions from '../../stores/login/login.actions';

import * as fromLangAction from '../../stores/lang/lang.actions';
import * as fromLangSelector from '../../stores/lang/lang.reducer';

// Style
import { faAsterisk, faSignOutAlt, faList } from '@fortawesome/free-solid-svg-icons';

// Components
import { LoginComponent } from 'src/app/auth/login/login.component';


/**
 * Headmenu Component.
 * 
 * Displays a navigation bar to be applied at the top of the main interface of the web application.
 */

@Component({
  selector: 'app-headmenu',
  templateUrl: './headmenu.component.html',
  styleUrls: ['./headmenu.component.css']
})
export class HeadmenuComponent implements OnInit {

  // constant values
  /**
   * list of navigation links to be added to the navigation bar
   */
  navLinks: NavLink[] = links;
  /**
   * list of possible application languages to translate the content
   */
  navLanguages: Language[] = languages;

  /**
   * flag to determine if navigation bar is collapsed for small screen compatibility
   */
  isCollapsed: boolean = true;

  // language
  /**
   * current language used in the app. Defaults to the first one of the languages list
   */
  language$: Observable<Language> = this.store.select(fromLangSelector.getLang);

  // auth
  /**
   * flag to determine user logged status
   */
  isLoggedIn: boolean = false;
  /**
   * flag to determine user permission status
   */
  hasPermission: boolean = false;

  /**
   * contribution list icon
   */
  listIcon = faList;
  /**
   * password change icon
   */
  passwordIcon = faAsterisk;
  /**
   * logout icon
   */
  logoutIcon = faSignOutAlt;

  /**
   * user name information
   */
  userName: string = '';
  /**
   * user email information
   */
  userEmail: string = '';

  /**
   * Constructor for the navigation bar. Initializes the user logged status and permissions status.
   * @param modalService Bootstrap modal service
   * @param authServ authentication service
   * @param userServ user service
   * @param changeDet change detection
   * @param langActions Redux language actions
   */
  constructor(
    private modalService: NgbModal,
    //private authServ: AuthService,
    //private userServ: UserService,
    private store: Store<AppState>,
    private router: Router,
    private changeDet: ChangeDetectorRef) {
    //private langActions: LangActions) {

    // check if user is logged in
    //this.isLoggedIn = this.authServ.isLoggedIn();

    // check if user has permissions
    //if (this.isLoggedIn) this.hasPermission = this.checkPermission();
  }

  /**
   * Calls the methods to subscribe to redux updates and to get user information to display in the template.
   */
  ngOnInit(): void {
    // login state
    this.store
      .select(loginSelector.getLoginStatus)
      .subscribe((lstatus: boolean) => {
        this.isLoggedIn = lstatus;
      });
  }

  /**
   * Method called when the user selects an app language in the dropdown menu.
   * 
   * Dispatches an action with Redux to update the language. See {@link langActions} for more details about the dispatch.
   * @param language language selected by the user
   */
  selectLanguage(language: Language) {
    this.store.dispatch(fromLangAction.GetLanguage({payload: language}));
  }

  /**
   * Opens the login Bootstrap modal with the login content.
   * See {@link LoginComponent} for more details. 
   */
  openLogin() {
    if (!this.isLoggedIn) {
      this.modalService.open(LoginComponent, { centered: true});
    }
  }

  /**
   * Logs out the user and updates the logged status.
   * Uses the authentication service to logout. See {@link AuthService} for more details.
   */
  logout() {
    this.store.dispatch(loginActions.LogoutUser());
    this.router.navigate(['/']);
  }

}
