import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Style
import { faAsterisk, faSignOutAlt, faList } from '@fortawesome/free-solid-svg-icons';

// Interfaces and Constants
import { NavLink } from 'src/app/interfaces/navLink';
import { Language } from 'src/app/interfaces/language';
import { links } from '../../constants/navLinks';
import { languages } from '../../constants/languages';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';
import { UserService } from 'src/app/serv/rest/users/user.service';

// Redux
import { select } from '@angular-redux/store';
import { Observable } from 'rxjs';
import { selectLanguage, selectUser } from 'src/app/redux/selectors';
import { LangActions } from 'src/app/redux/actions/langActions';

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
  selectedLanguage: Language = this.navLanguages[0];

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
   * holds redux subscription to update user information
   */
  @select(selectUser) userRedux$!: Observable<any>;
  /**
   * holds redux subscription to update the current app language
   */
  @select(selectLanguage) language$!: Observable<boolean>;

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
    private authServ: AuthService,
    private userServ: UserService,
    private changeDet: ChangeDetectorRef,
    private langActions: LangActions) {

    // check if user is logged in
    this.isLoggedIn = this.authServ.isLoggedIn();

    // check if user has permissions
    if (this.isLoggedIn) this.hasPermission = this.checkPermission();
  }

  /**
   * Calls the methods to subscribe to redux updates and to get user information to display in the template.
   */
  ngOnInit(): void {
    // improve UX with redux
    this.subscribeToRedux();

    // get user information to display
    this.getUserInformation();
  }

  /**
   * Checks the user role and determines the permissions status.
   * @returns true if user has a 'superuser' or 'fireloc' role, false if otherwise.
   */
  checkPermission() {
    let userRole = localStorage.getItem('user_role');
    if (userRole === 'superuser' || userRole === 'fireloc') return true;
    else return false;
  }

  /**
   * Subscribe to redux events.
   * Subscribes to update user information and app language when needed.
   */
  subscribeToRedux() {
    this.userRedux$.subscribe(
      (user: any) => {
        // update information displayed after profile update
        this.getUserInformation();
        this.changeDet.detectChanges();
      }
    );
    // update the language used in the app
    this.language$.subscribe(
      (language: any) => {
        switch (language) {
          case 'pt': this.selectedLanguage = this.navLanguages[0]; break;
          case 'en': this.selectedLanguage = this.navLanguages[1]; break;
        }
      }
    );
  }

  /**
   * Gets the user information from API.
   * Uses the authentication service to determine if the user is logged in and the user service to obtain the user name and email.
   * 
   * See {@link AuthService} and {@link UserService} for more details on the services.
   */
  getUserInformation() {
    // check if user is logged in
    this.isLoggedIn = this.authServ.isLoggedIn();

    if (this.isLoggedIn) {
      // get user information
      this.userServ.getUser().subscribe(
        (result: any) => {
          this.userName = result.first_name + ' ' + result.last_name;
          this.userEmail = result.email;
        }, error => { }
      );
    }
  }

  /**
   * Method called when the user selects an app language in the dropdown menu.
   * 
   * Dispatches an action with Redux to update the language. See {@link langActions} for more details about the dispatch.
   * @param language language selected by the user
   */
  selectLanguage(language: Language) {
    this.selectedLanguage = language;
    // change language with redux action dispatch
    switch (this.selectedLanguage.country) {
      case 'pt': this.langActions.changeLanguage('pt'); break;
      case 'gb': this.langActions.changeLanguage('en'); break;
    }
  }

  /**
   * Opens the login Bootstrap modal with the login content.
   * See {@link LoginComponent} for more details. 
   */
  openLogin() { this.modalService.open(LoginComponent, { centered: true }); }

  /**
   * Logs out the user and updates the logged status.
   * Uses the authentication service to logout. See {@link AuthService} for more details.
   */
  logout() {
    this.authServ.logout();
    this.isLoggedIn = this.authServ.isLoggedIn();
  }
}
