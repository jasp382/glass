import { Component, Input, OnInit } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';
import { Router } from '@angular/router';

// Style
import { faEnvelope, faAsterisk, faEye, faEyeSlash, faUser } from '@fortawesome/free-solid-svg-icons';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

// Redux
import { UserActions } from 'src/app/redux/actions/userActions';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';

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
    private authServ: AuthService,
    private router: Router,
    private userActions: UserActions
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
      this.nameValue = this.registerForm.get('name')?.value;
      this.lastNameValue = this.registerForm.get('lastName')?.value;
      this.emailValue = this.registerForm.get('email')?.value;
      this.passwordValue = this.registerForm.get('password')?.value;
      this.confirmationValue = this.registerForm.get('confirmation')?.value;

      // register user
      this.registerUser();
    }
  }

  /**
   * Registers a new user in the FireLoc system with the authentication service. 
   * Also sends a registration confirmation to the user's email after a successful registration in the system.
   * 
   * Successful process ends with a call to a method to perform the user login.
   */
  registerUser() {
    // register new user
    this.authServ.registerUser(this.nameValue, this.lastNameValue, this.emailValue, this.passwordValue)
      .subscribe(
        (result: any) => {
          // send registration email
          this.authServ.sendRegistrationConfirmation(this.emailValue).subscribe(
            (result: any) => { }, error => { }
          );
          // login
          this.login();
          this.modal.close(); 
        }, error => { }
      );
  }

  /**
   * Logs in a user after the account creation. 
   * Upon successful login, stores necessary information in the browser's local storage and redirects the user to the Geoportal.
   * 
   * Dispatches the user action to allow other components to update user information as needed. See {@link UserActions}.
   */
  login() {
    this.authServ.login(this.emailValue, this.passwordValue).subscribe(
      (result: any) => {
        let access_token: string = result.access_token;
        let refresh_token: string = result.refresh_token;
        let type_token: string = result.token_type;
        let expiration: string = result.expires_in;
        let role: string = result.role;
        let userId: string = this.emailValue;
        let date: any = Date.now();

        if (access_token && refresh_token && type_token && expiration && userId && date && role) {
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          localStorage.setItem('type_token', type_token);
          localStorage.setItem('expiration', expiration);
          localStorage.setItem('userId', userId);
          localStorage.setItem('login_time', date.toString());
          localStorage.setItem('user_role', role);

          // get remember session value
          let shouldRemember = this.registerForm.get('rememberSession')?.value;
          this.authServ.setRememberUser(shouldRemember);

          // redirect to geoportal
          this.router.navigate(['/geoportal']);

          // dispatch redux action to update user information
          this.userActions.getUserInfo();
        };
      }, error => { }
    );
  }
}
