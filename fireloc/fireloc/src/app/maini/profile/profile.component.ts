import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';
import { Observable } from 'rxjs';

// Routing
import { Router } from '@angular/router';

// Style
import { faAsterisk, faUser, faList, faTimes } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Services
import { UserService } from 'src/app/serv/rest/users/user.service';
import { ContribService } from 'src/app/serv/rest/contrib.service';
import { AuthService } from 'src/app/serv/rest/users/auth.service';

// Interfaces
import { UserProfile } from 'src/app/interfaces/users';
import { Contribution, Geom, ContribDate } from 'src/app/interfaces/contribs';

// Redux
import { UserActions } from 'src/app/redux/actions/userActions';
import { select } from '@angular-redux/store';
import { selectLanguage } from 'src/app/redux/selectors';

// Util
import { avgLatLong, getDateTimeValues, getLatLongValues } from 'src/app/util/helper';

/**
 * Default contribution photo when none is available
 */
const defaultContribPhoto = 'data:image/jpg;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAQAAADa613fAAAAaElEQVR42u3PQREAAAwCoNm/9CL496ABuREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREWkezG8AZQ6nfncAAAAASUVORK5CYII=';

/**
 * Geoportal Profile component.
 * 
 * Allows a user to view their information and change it, including their password.
 * It also displays a list of user contributions with their associated event, if one has been identified.
 * 
 * Some functionality is incomplete due to API unavailability.
 * 
 */
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
  userInfo: UserProfile = {
    email: '',
    firstName: '',
    lastName: '',
    password: ''
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

  /**
   * Redux selector for the language state
   */
  @select(selectLanguage) langRedux$!: Observable<any>;

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
    private userServ: UserService,
    private authServ: AuthService,
    private contribServ: ContribService,
    private modalService: NgbModal,
    private userActions: UserActions
  ) {
    // set input validation for profile
    this.profileForm = new FormGroup({
      firstName: new FormControl(this.userInfo.firstName, [Validators.required, Validators.maxLength(50)]),
      lastName: new FormControl(this.userInfo.lastName, [Validators.required, Validators.maxLength(50)])
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
    // check if user contributions are in local storage
    let contributions = localStorage.getItem("userContributions");
    if (contributions !== null) {
      this.userContributions = JSON.parse(contributions);
    }

    // get language updates (for contributions)
    this.subscribeToRedux();

    // get user information
    this.getUserInfo();

    // activate correct tab
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
      this.getUserContribs();
      this.activeTab = 1;
    }

  }

  /**
   * Subscribe to Redux to get updates about the current language used in the app
   */
  subscribeToRedux() {
    // subscribe to get app language changes
    this.langRedux$.subscribe((language: string) => { this.language = language; });
  }

  /**
   * Changes URL on tab click
   * @param path 
   */
  navigate(path: string) { this.router.navigate([path]); }

  /**
   * Gets the user's information from the API and updates the profile form.
   */
  getUserInfo() {
    this.userServ.getUser().subscribe(
      (result: any) => {
        this.userInfo.firstName = result.first_name;
        this.userInfo.lastName = result.last_name;
        this.userInfo.email = result.email;

        // update form values
        this.profileForm.setValue({
          firstName: this.userInfo.firstName,
          lastName: this.userInfo.lastName
        });
      }, error => { }
    );
  }

  /**
   * Updates the user's information with the API. 
   * 
   * Dispatches a user action to allow other components to update the user information.
   * See {@link UserActions} for more information.
   */
  updateUserInfo() {
    let data = { first_name: this.userInfo.firstName, last_name: this.userInfo.lastName, }
    this.userServ.updateUser(this.userInfo.email, data).subscribe(
      (result: any) => {
        // dispatch redux action to update information in navbar
        this.userActions.getUserInfo();
      }, error => { }
    );
  }

  /**
   * Changes the user's password with the API.
   */
  changePassword() {
    let data = { password: this.userInfo.password };
    this.userServ.updateUser(this.userInfo.email, data).subscribe((result: any) => { }, error => { });
  }

  /**
   * Method called by submitting the profile form to update the user's information.
   * 
   * Checks whether the form is valid and calls the method to change information with the API.
   */
  changeUserInfo() {
    // assert that form is valid
    if (this.profileForm.valid) {
      // update information from inputs
      this.userInfo.firstName = this.firstName?.value;
      this.userInfo.lastName = this.lastName?.value;

      // update profile information
      this.updateUserInfo();
    }
  }

  /**
   * Method called by submitting the password form to update the user's password.
   * 
   * Checks whether the form is valid and calls the method to change password with the API.
   */
  changeUserPassword() {
    // assert that form is valid
    if (this.passwordForm.valid) {
      // update information from inputs
      this.userInfo.password = this.newPasswordValue?.value;
      // update user password
      this.changePassword();
    }
  }

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
  deleteAccount() {
    this.hasClickedRemove = true;
    // without checked confirmation, show error
    if (this.isConfChecked) {

      // remove user with API
      this.userServ.deleteUser(this.userInfo.email).subscribe((result: any) => { this.authServ.logout(); }, error => { });

      // close
      this.modalService.dismissAll();
    }
  }

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
   * Gets the user's contributions with the API, if there are no user contributions already stored.
   */
  getUserContribs() {
    // check if contributions are stored
    if (this.userContributions.length === 0) {
      // get user contributions from API
      let userID = localStorage.getItem('userId');
      this.contribServ.getContributions(userID).subscribe(
        async (result: any) => {
          for (let contrib of result.data) {
            // get initial contribution values
            let id = contrib.fid;
            let pic = contrib.pic;

            let location = '';
            if (this.language === 'pt') location = contrib.fire_name ? contrib.fire_name : 'Sem Localização';
            else location = contrib.fire_name ? contrib.fire_name : 'No Location'; // language 'en'

            let [year, month, day, hour, minute] = getDateTimeValues(contrib.datehour, true, this.language);
            let date: ContribDate = { year: year, month: month, day: day };
            let dir = contrib.direction;
            let dsun = contrib.dsun;

            let photoBase64: string = await this.getContribPhoto(pic);

            // create contribution object
            var contribution: Contribution = {
              fid: id,
              pic: photoBase64,
              location: location,
              date: date,
              hour: hour,
              minute: minute,
              dir: dir,
              dsun: dsun,
              geom: [],
              avgLat: 0,
              avgLong: 0
            };

            // get geom info
            for (let geom of contrib.geom) {
              let pid = geom.pid;
              let [lat, long] = getLatLongValues(geom.geom);

              // create point object
              let point: Geom = { pid: pid, lat: lat, long: long };

              // add point to contribution object
              contribution.geom.push(point);
            }

            // get average coordinates data
            let lat, long: string;
            [lat, long] = avgLatLong(contribution.geom);
            contribution.avgLat = lat;
            contribution.avgLong = long;

            // add contribution to list of user contributions
            this.userContributions.push(contribution);
          }

          // save contributions in local storage
          localStorage.setItem("userContributions", JSON.stringify(this.userContributions));

          // finished loading contributions
          this.loadingContribs = false;
        },
        error => {
          // finished loading contributions
          this.loadingContribs = false;
          this.contribError = true;
        }
      );
    } else {
      // finished loading contributions
      this.loadingContribs = false;
    }
  }

  /**
   * Gets a contribution photo with the API. If no photo is available, it returns the default.
   * @param photoName name of the contribution photo
   * @returns contirbution photo or default if none available
   */
  getContribPhoto(photoName: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.contribServ.getContributionPhoto(photoName).subscribe(
        (result: any) => {
          // get photo data
          let photoEncoded = result.data;
          let photoData: string = 'data:image/jpg;base64,' + photoEncoded;

          // resolve promise to continue execution
          resolve(photoData);
        },
        error => {
          resolve(defaultContribPhoto);
          // finished loading contributions
          this.loadingContribs = false;
          this.contribError = true;
        }
      );
    })
  }

  /**
   * Opens the user contribution's photo in a Bootstrap modal.
   * @param content modal content to display
   * @param contrib contribution associated with the photo
   */
  openContribPhoto(content: any, contrib: Contribution) {
    // set the information to be displayed
    this.openContribLocation = contrib.location;
    this.openContribImage = contrib.pic;

    // open the modal
    this.modalService.open(content, { centered: true, size: 'xl' })
      .result.then(() => { }, () => {
        // reset variables when popup is closed
        this.openContribLocation = '';
        this.openContribImage = defaultContribPhoto;
      });
  }

  /**
   * Opens user contribution's event information
   */
  openEvent() { this.isEventOpen = true; }

  /**
   * Closes user contribution's event information
   */
  closeEvent() { this.isEventOpen = false; }

}
