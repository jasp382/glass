import { Component, OnInit } from '@angular/core';

import { AbstractControl, FormControl, FormGroup, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';
import { Observable } from 'rxjs';

// Routing
import { Router } from '@angular/router';

// Style
import { faAsterisk, faUser, faList, faTimes } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces
import { UserProfile, User } from 'src/app/interfaces/users';
import { Contribution, Geom, ContribDate } from 'src/app/interfaces/contribs';
import { Token } from 'src/app/interfaces/general';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as loginSelector from '../../stores/login/login.reducer';
import * as loginActions from '../../stores/login/login.actions';

// Util
import { avgLatLong, getDateTimeValues, getLatLongValues } from 'src/app/util/helper';

/**
 * Default contribution photo when none is available
 */
const defaultContribPhoto = 'data:image/jpg;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAQAAADa613fAAAAaElEQVR42u3PQREAAAwCoNm/9CL496ABuREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREWkezG8AZQ6nfncAAAAASUVORK5CYII=';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {

  /**
   * current active tab in the profile
   */
  activeTab: number = 1;

  /**
   * flag to determine if user contributions are being loaded
   */
  loadingContribs: boolean = true;

  /**
   * current app language
   */
  language: string = 'pt';

  // icons
  /**
   * icon for user contribution list
   */
  listIcon = faList;
  /**
   * icon for user profile
   */
  userIcon = faUser;
  /**
   * icon for passwords
   */
  passwordIcon = faAsterisk;
  /**
   * icon to close information
   */
  closeIcon = faTimes;

  /**
   * user information: email, first name, last name, and password
   */
  userInfo: User = {
    id: 0,
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    token: [],
    usgroup: {
      id: 0, name: '', users: null, layers: null
    },
    attr: [],
    active: false
  };

  // password information
  /**
   * new password value. Used for changing a user account's password
   */
  newPassword: string = '';
  /**
   * password confirmation value. Used for changing a user account's password
   */
  passwordConfirmation: string = '';

  /**
   * profile information inputs
   */
  profileForm!: FormGroup;

  /**
   * password change inputs
   */
  passwordForm!: FormGroup;

  /**
   * flag to determine if an event's information is being displayed
   */
  isEventOpen: boolean = false;

  // contributions list information
  /**
   * list of user contributions
   */
  userContributions: Contribution[] = [];
  /**
   * opened contribution location
   */
  openContribLocation: string = '';
  /**
   * opened contribution photo
   */
  openContribImage: string = defaultContribPhoto;

  /**
   * flag to determine if there has been an error while loading the user's contributions
   */
  contribError: boolean = false;

  // delete account
  /**
   * flag to determine if user has confirmed their account removal
   */
  isConfChecked: boolean = false;
  /**
   * flag to determine if the user has decided to remove their account
   */
  hasClickedRemove: boolean = false;

  token: Token|null = null;
  userID: string = '';

  /**
   * Profile component constructor. Initializes the profile form controls and password change form controls.
   * @param router Angular router
   * @param userServ user service. See {@link UserService}.
   * @param authServ authentication service. See {@link AuthService}.
   * @param contribServ contribution service. See {@link ContribService}.
   * @param modalService Bootstrap modal service
   * @param userActions user actions. See {@link UserActions}.
   */
  constructor(
    private router: Router,
    private store: Store<AppState>,
    //private userServ: UserService,
    //private authServ: AuthService,
    //private contribServ: ContribService,
    private modalService: NgbModal,
    //private userActions: UserActions
  ) {
    // set input validation for profile
    this.profileForm = new FormGroup({
      firstName: new FormControl(this.userInfo.first_name, [Validators.required, Validators.maxLength(50)]),
      lastName: new FormControl(this.userInfo.last_name, [Validators.required, Validators.maxLength(50)])
    });

    // set input validation for password
    this.passwordForm = new FormGroup({
      newPassword: new FormControl('', [Validators.required]),
      passwordConfirmation: new FormControl('', [Validators.required])
    }, { validators: this.passwordsValidator });
  }

  /**
   * Validator for change password form. 
   * Checks whether the password input and password confirmation inputs match.
   * @param group form group with necessary inputs
   * @returns no errors (null) if password inputs match or 'notSame' error otherwise.
   */
  passwordsValidator: ValidatorFn = (group: AbstractControl): ValidationErrors | null => {
    // get values
    let pass = group.get('newPassword')?.value;
    let confirmPass = group.get('passwordConfirmation')?.value

    // validate
    return pass === confirmPass ? null : { notSame: true }
  }

  /**
   * Checks whether user contributions are stored in the browser's local storage. If no contributions are present, load them from the API.
   * 
   * Subscribes to Redux for updates.
   * Gets the user account's information.
   * Checks the URL to activate the correct page tab.
   */
  ngOnInit(): void {
    // Get User current state
    this.store
      .select(loginSelector.getLogUser)
      .subscribe((user: User|null) => {
        if (user !== null) {
          this.userInfo = user;
        } else {
          // We need to update User state
          if (this.token === null && this.userID === '') {
            this.store
              .select(loginSelector.getTokenUserID)
              .subscribe((payload: any) => {
                this.token = payload.token;
                this.userID = payload.userid !== null ? payload.userid : '';

                if (this.token !== null && this.userID !== '') {
                  this.store.dispatch(loginActions.LoggedUser(
                    { payload: {token: this.token, userid: this.userID} }
                  ))
                }
              })
          } else if (this.token !== null && this.userID !== '') {
            this.store.dispatch(loginActions.LoggedUser(
              { payload: {token: this.token, userid: this.userID} }
            ));
          }
        }
      })

    this.checkUrl();
  }

  /**
   * Activates correct tab with URL from Angular router
   */
  checkUrl() {
    // get last part of url
    var urlSegment = this.router.url.split('/').pop();

    // check which tab should be active
    if (urlSegment === 'password')
      this.activeTab = 3;
    else if (urlSegment === 'profile')
      this.activeTab = 2;
    else {
      // get user contributions
      //this.getUserContribs();
      this.activeTab = 1;
    }

  }

  /**
   * Changes URL on tab click
   * @param path 
   */
  navigate(path: string) { this.router.navigate([path]); }

  /**
   * Updates the user's information with the API. 
   * 
   * Dispatches a user action to allow other components to update the user information.
   * See {@link UserActions} for more information.
   */
  updateUserInfo() {}

  /**
   * Changes the user's password with the API.
   */
  changePassword() {}

  /**
   * Method called by submitting the profile form to update the user's information.
   * 
   * Checks whether the form is valid and calls the method to change information with the API.
   */
  changeUserInfo() {
    // assert that form is valid
    if (this.profileForm.valid) {
      // update information from inputs
      this.userInfo.first_name = this.firstName?.value;
      this.userInfo.last_name = this.lastName?.value;

      // update profile information
      //this.updateUserInfo();
    }
  }

  /**
   * Method called by submitting the password form to update the user's password.
   * 
   * Checks whether the form is valid and calls the method to change password with the API.
   */
  changeUserPassword() { }

  /**
   * Opens the account removal confirmation Bootstrap modal.
   * @param content modal content to display
   */
  openDeleteModal(content: any) {
    // reset variables for new modal
    this.isConfChecked = false;
    this.hasClickedRemove = false;

    // open modal
    this.modalService.open(content, { centered: true, size: 'lg' });
  }

  /**
   * Checks whether the user has confirmed their account removal before proceeding.
   * 
   * If confirmation has been obtained, it removes and logs out the user with the API.
   */
  deleteAccount() {}

  /**
   * getter for profile form control for user's first name
   */
  get firstName() { return this.profileForm.get('firstName'); }
  /**
   * getter for profile form control for user's surnames
   */
  get lastName() { return this.profileForm.get('lastName'); }

  /**
   * getter for password form control for user's new password
   */
  get newPasswordValue() { return this.passwordForm.get('newPassword'); }
  /**
   * getter for password form control for user's new password confirmation
   */
  get passwordConfirmationValue() { return this.passwordForm.get('passwordConfirmation'); }

  /**
   * Opens user contribution's event information
   */
  openEvent() { this.isEventOpen = true; }

  /**
   * Closes user contribution's event information
   */
  closeEvent() { this.isEventOpen = false; }

}
