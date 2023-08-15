import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

// Style
import { faEnvelope, faAsterisk, faEyeSlash, faEye } from '@fortawesome/free-solid-svg-icons';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as fromLoginAction from '../../stores/login/login.actions';
import * as fromLoginSelector from '../../stores/login/login.reducer';

// Components
import { ForgotpassComponent } from '../forgotpass/forgotpass.component';
import { Login, Token } from 'src/app/interfaces/login';
import { Observable } from 'rxjs';


/**
 * Login component.
 * 
 * Displays content meant for a Bootstrap modal to login a user with their credentials.
 */
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  /**
   * login modal reference
   */
  modal: NgbActiveModal;

  userid: string = '';

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
   * email value from login form
   */
  emailValue: string = '';
  /**
   * password value from login form
   */
  passwordValue: string = '';
  /**
   * flag to check form submission status
   */
  submitted = false;
  /**
   * form reference to login a user
   */
  loginForm!: FormGroup;

  /**
   * Login Token Selector
   */
  loginToken$: Observable<Token | null> = this.store.select(fromLoginSelector.getLoginToken);
  initialToken: boolean = true;

  /**
   * Constructor for the login component.
   * Initializes the login modal reference from Bootstrap Active Modal.
   * @param modal active modal from Bootstrap
   * @param modalService modal management service from Bootstrap
   * @param authServ authentication service
   * @param router Angular router
   * @param userActions Redux user actions
   */
  constructor(
    modal: NgbActiveModal,
    private store: Store<AppState>,
    private modalService: NgbModal,
    //private authServ: AuthService,
    private router: Router,
    //private userActions: UserActions,
  ) { this.modal = modal; }

  /**
   * Initializes the form to login a user with necessary controls and validators.
   */
  ngOnInit(): void {
    this.loginForm = new FormGroup({
      email: new FormControl(this.emailValue, [
        Validators.required,
        Validators.email,
        Validators.maxLength(254)
      ]),
      password: new FormControl(this.passwordValue, [Validators.required]),
      rememberSession: new FormControl(false, [])
    });

    this.redirect();
  }

  /**
   * Opens the forgot password modal and closes the login modal. See {@link ForgotpassComponent}
   */
  forgotPassword() {}

  /**
   * Method called upon form submission.
   * 
   * Checks whether form is valid, gets the user credentials and calls the method to perform the login.
   */
  onSubmit() {
    if (this.loginForm.valid) {
      this.submitted = true;

      // get form values
      this.emailValue = this.loginForm.get('email')?.value;
      this.passwordValue = this.loginForm.get('password')?.value;

      // log in user
      this.logIn(this.emailValue, this.passwordValue);
    }
  }

  /**
   * Performs the user login. Upon successful login, stores necessary information in the browser's local storage.
   * 
   * Calls the method to redirect the user according to their role.
   * @param email user email from login form
   * @param password user password from login form
   */
  logIn(email:string, password: string) {
    this.userid = email;
    let _login: Login = {userid: email, password: password};

    this.store.dispatch(fromLoginAction.LoginUser({payload: _login}));
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
    this.loginToken$.subscribe(
      (token: Token | null) => {
        // close the login modal
        if (!this.initialToken) {
          this.modal.close();
        }

        if (token !== null) {
          let date: any = Date.now()
          localStorage.setItem('access_token', token.access_token);
          localStorage.setItem('refresh_token', token.refresh_token);
          localStorage.setItem('type_token', token.token_type);
          localStorage.setItem('expiration', token.expires_in.toString());
          localStorage.setItem('userId', this.userid);
          localStorage.setItem('scope', token.scope);
          localStorage.setItem('login_time', date.toString());
          localStorage.setItem('user_role', token.role);

          this.store.dispatch(fromLoginAction.UpdateUserID({payload: this.userid}));

          switch (token.role) {
            case 'superuser':
            case 'fireloc':
              this.router.navigate(['/admin']);
              break;
            //navigate to geoportal
            default:
              this.router.navigate(['/geoportal']);
          }
        }

        this.initialToken = false;
      }
    )
  }

}
