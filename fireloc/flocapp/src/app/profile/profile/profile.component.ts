import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';


// Interfaces
import { UserProfile, User } from 'src/app/interfaces/users';
import { Token } from 'src/app/interfaces/general';


// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as loginSelector from '../../stores/login/login.reducer';
import * as loginActions from '../../stores/login/login.actions';


@Component({
  selector: 'prof-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {

  /**
   * profile information inputs
   */
  profileForm!: FormGroup;

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

  token: Token|null = null;
  userID: string = '';

  constructor(private store: Store<AppState>) {
    // set input validation for profile
    this.profileForm = new FormGroup({
      firstName: new FormControl(this.userInfo.first_name, [Validators.required, Validators.maxLength(50)]),
      lastName: new FormControl(this.userInfo.last_name, [Validators.required, Validators.maxLength(50)])
    });
  }

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
  }

  /**
   * Updates the user's information with the API. 
   * 
   * Dispatches a user action to allow other components to update the user information.
   * See {@link UserActions} for more information.
   */
  updateUserInfo() {}

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
   * getter for profile form control for user's first name
   */
  get firstName() { return this.profileForm.get('firstName'); }
  /**
   * getter for profile form control for user's surnames
   */
  get lastName() { return this.profileForm.get('lastName'); }

}
