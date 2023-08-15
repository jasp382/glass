import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';

// Font Awesome
import { faEnvelope, faAsterisk, faEyeSlash, faEye } from '@fortawesome/free-solid-svg-icons';

// Bootstrap
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';

/**
 * Reset password component.
 * 
 * Displays content meant for a Bootstrap modal to reset a user password.
 * This component should only be shown through an email with a link, providing a token for password change.
 * 
 * See {@link ForgotpassComponent} for information about initializing password recovery.
 */
@Component({
  selector: 'app-resetpass',
  templateUrl: './resetpass.component.html',
  styleUrls: ['./resetpass.component.css']
})
export class ResetpassComponent implements OnInit {

  /**
   * reset password modal reference
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
   * new password value from password form
   */
  passwordValue: string = '';
  /**
   * password confirmation value from password form
   */
  confirmationValue: string = '';
  /**
   * flag to check form submission status
   */
  submitted = false;
  /**
   * form reference to reset a user account's password
   */
  newPasswordForm!: FormGroup;

  /**
   * token received through the URL and provided to the modal. See {@link HomeComponent} for usage.
   */
  token: string = '';

  /**
   * Constructor for the reset password component.
   * Initializes the reset password modal reference from Bootstrap Active Modal.
   * @param modal active modal from Bootstrap
   * @param authServ authentication service
   */
  constructor(modal: NgbActiveModal, private authServ: AuthService) { this.modal = modal; }

  /**
   * Initializes the form to reset a user account's password with necessary controls and validators.
   */
  ngOnInit(): void {
    this.newPasswordForm = new FormGroup({
      password: new FormControl(this.passwordValue, [Validators.required]),
      passwordConfirmation: new FormControl(this.confirmationValue, [Validators.required])
    }, { validators: this.passwordsValidator });
  }

  /**
   * Validator for reset password form. 
   * Checks whether the new password input and password confirmation inputs match.
   * @param group form group with necessary inputs
   * @returns no errors (null) if password inputs match or 'notSame' error otherwise.
   */
  passwordsValidator: ValidatorFn = (group: AbstractControl): ValidationErrors | null => {
    // get values
    let pass = group.get('password')?.value;
    let confirmPass = group.get('passwordConfirmation')?.value

    // validate
    return pass === confirmPass ? null : { notSame: true }
  }

  /**
   * Method called upon form submission.
   * 
   * Checks whether form is valid, gets the password value and calls the method to perform the password change.
   */
  onSubmit() {
    if (this.newPasswordForm.valid) {
      this.submitted = true;

      this.passwordValue = this.newPasswordForm.get('password')?.value;
      this.confirmationValue = this.newPasswordForm.get('passwordConfirmation')?.value;

      // change user password
      this.changePassword(this.token, this.passwordValue);
    }
  }

  /**
   * Changes the user's account password with the authentication service.
   * @param token token user received in the account recovery email
   * @param newPassword new password to update on the user's credentials
   */
  changePassword(token: string, newPassword: string) {
    this.authServ.changePassword(token, newPassword).subscribe((result: any) => { this.modal.close(); }, error => { });
  }

}
