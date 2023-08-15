import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

// Style
import { faEnvelope, faAsterisk, faEyeSlash, faEye } from '@fortawesome/free-solid-svg-icons';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Components
import { ForgotpassComponent } from '../forgotpass/forgotpass.component';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';

// Redux
import { UserActions } from 'src/app/redux/actions/userActions';

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
    private modalService: NgbModal,
    private authServ: AuthService,
    private router: Router,
    private userActions: UserActions,
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
  }

  /**
   * Opens the forgot password modal and closes the login modal. See {@link ForgotpassComponent}
   */
  forgotPassword() {
    // close login modal
    this.modal.close();

    // open forgot modal
    this.modalService.open(ForgotpassComponent, { centered: true });
  }

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
  logIn(email: string, password: string) {
    this.authServ.login(email, password).subscribe(
      (result: any) => {
        let accessToken: string = result.access_token;
        let refreshToken: string = result.refresh_token;
        let typeToken: string = result.token_type;
        let expiration: string = result.expires_in;
        let role: string = result.role;
        let userId: string = email;
        let date: any = Date.now();

        if (accessToken && refreshToken && typeToken && expiration && userId && date && role) {
          localStorage.setItem('access_token', accessToken);
          localStorage.setItem('refresh_token', refreshToken);
          localStorage.setItem('type_token', typeToken);
          localStorage.setItem('expiration', expiration);
          localStorage.setItem('userId', userId);
          localStorage.setItem('login_time', date.toString());
          localStorage.setItem('user_role', role);

          // get remember session value
          let shouldRemember = this.loginForm.get('rememberSession')?.value;
          this.authServ.setRememberUser(shouldRemember);

          // redirect user according to role
          this.redirect(role);
        };
      }, error => { }
    );
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
  redirect(role: string) {
    // close the login modal
    this.modal.close();

    // dispatch redux action to update user information
    this.userActions.getUserInfo();

    switch (role) {
      // navigate to backoffice
      case 'superuser':
      case 'fireloc':
        this.router.navigate(['/admin']);
        break;
      // navigate to geoportal
      default:
        this.router.navigate(['/geoportal']);
    }
  }
}
