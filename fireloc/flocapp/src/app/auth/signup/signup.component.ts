import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';
import { Router } from '@angular/router';

// Style
import { faEnvelope, faAsterisk, faEye, faEyeSlash, faUser } from '@fortawesome/free-solid-svg-icons';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces
import { NewUser } from 'src/app/interfaces/users';
import { Login, Token } from 'src/app/interfaces/login';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as loginSelector from '../../stores/login/login.reducer';
import * as loginActions from '../../stores/login/login.actions';
import { Observable } from 'rxjs';

/**
 * Signup component.
 * 
 * Displays content meant for a Bootstrap modal to register a new user account in the FireLoc system.
 */
@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent implements OnInit {

  /**
   * register modal reference
   */
  modal: NgbActiveModal;

  /**
   * user name inputs icon
   */
  userIcon = faUser;
  /**
   * email input icon
   */
  emailIcon = faEnvelope;
  /**
   * password input icon
   */
  passwordIcon = faAsterisk;
  /**
   * visible password icon
   */
  showIcon = faEye;
  /**
   * hidden password icon
   */
  hideIcon = faEyeSlash;

  /**
   * first name value from register form
   */
  nameValue: string = '';
  /**
   * surnames value from register form
   */
  lastNameValue: string = '';
  /**
   * email value from register form
   */
  emailValue: string = '';
  /**
   * password value from register form
   */
  passwordValue: string = '';
  /**
   * password confirmation value from register form
   */
  confirmationValue: string = '';
  /**
   * flag to check form submission status
   */
  submitted = false;
  /**
   * form reference to register a new user in the FireLoc system.
   */
  registerForm!: FormGroup;

  recordUser$: Observable<string> = this.store.select(loginSelector.getRecordUser);
  loginToken$: Observable<Token|null> = this.store.select(loginSelector.getLoginToken);
  initialToken: boolean = true;

  recordUser: string = '';

  /**
   * Constructor for the signup component.
   * Initializes the register modal reference from Bootstrap Active Modal.
   * @param modal active modal from Bootstrap
   * @param authServ authentication service
   * @param router Angular router
   * @param userActions Redux user actions
   */
  constructor(
    modal: NgbActiveModal,
    private store: Store<AppState>,
    //private authServ: AuthService,
    private router: Router,
    //private userActions: UserActions
  ) { this.modal = modal; }

  /**
   * Initializes the form to register a new user account with necessary controls and validators.
   */
  ngOnInit(): void {
    this.registerForm = new FormGroup({
      name: new FormControl(this.nameValue, [Validators.required]),
      lastName: new FormControl(this.nameValue, [Validators.required]),
      email: new FormControl(this.emailValue, [
        Validators.required, Validators.email,
        Validators.pattern('^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,4}$'), // require top-level domain (.com, .uk, ...)
      ]),
      password: new FormControl(this.passwordValue, [Validators.required]),
      confirmation: new FormControl(this.confirmationValue, [Validators.required]),
      rememberSession: new FormControl(false, [])
    }, { validators: this.passwordsValidator });

    this.login();
    this.redirect();
  }

  /**
   * Validator for reset password form. 
   * Checks whether the password input and password confirmation inputs match.
   * @param group form group with necessary inputs
   * @returns no errors (null) if password inputs match or 'notSame' error otherwise.
   */
  passwordsValidator: ValidatorFn = (group: AbstractControl): ValidationErrors | null => {
    // get values
    let pass = group.get('password')?.value;
    let confirmPass = group.get('confirmation')?.value

    // validate
    return pass === confirmPass ? null : { notSame: true }
  }

  /**
   * Method called upon form submission.
   * 
   * Checks whether form is valid, gets the input values and calls the method to perform the account registration.
   */
  onSubmit() {
    if (this.registerForm.valid) {
      this.submitted = true;

      // get form values
      this.passwordValue = this.registerForm.get('password')?.value;

      // register user
      let nuser: NewUser = {
        name     : this.registerForm.get('name')?.value,
        lastName : this.registerForm.get('lastName')?.value,
        email    : this.registerForm.get('email')?.value,
        password : this.registerForm.get('password')?.value
      }
      this.registerUser(nuser);
    }
  }

  /**
   * Registers a new user in the FireLoc system with the authentication service. 
   * Also sends a registration confirmation to the user's email after a successful registration in the system.
   * 
   * Successful process ends with a call to a method to perform the user login.
   */
  registerUser(newUser: NewUser) {
    this.store.dispatch(loginActions.RegisterUser({ payload: newUser }));
  }

  /**
   * Logs in a user after the account creation. 
   * Upon successful login, stores necessary information in the browser's local storage and redirects the user to the Geoportal.
   * 
   * Dispatches the user action to allow other components to update user information as needed. See {@link UserActions}.
   */
  login() {
    this.recordUser$.subscribe((ruser: string) => {
      if (ruser !== '') {
        this.recordUser = ruser;

        let _login: Login = {userid: ruser, password: this.passwordValue};

        this.store.dispatch(loginActions.LoginUser({payload: _login}));
      }
    });
  }

  /**
   * Redirects the user according to their user role in the FireLoc system.
   * 
   * 'superuser' and 'fireloc' users are redirected to the Backoffice administration interface 
   * and other users are redirected to the Geoportal.
   * 
   * Dispatches the user action to allow other components to update user information as needed. See {@link UserActions}.
   * @param role use role
   */
  redirect() {
    this.loginToken$.subscribe((token: Token|null) => {
      if (token !== null) {
        this.modal.close()
        let date: any = Date.now()
          localStorage.setItem('access_token', token.access_token);
          localStorage.setItem('refresh_token', token.refresh_token);
          localStorage.setItem('type_token', token.token_type);
          localStorage.setItem('expiration', token.expires_in.toString());
          localStorage.setItem('userId', this.recordUser);
          localStorage.setItem('scope', token.scope);
          localStorage.setItem('login_time', date.toString());
          localStorage.setItem('user_role', token.role);

          this.store.dispatch(loginActions.UpdateUserID({payload: this.recordUser}));

          this.router.navigate(['/geoportal']);
      }
    })
  }


}
