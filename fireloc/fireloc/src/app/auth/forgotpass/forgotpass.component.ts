import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

// Style
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { faEnvelope } from '@fortawesome/free-solid-svg-icons';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';

/**
 * Forgot password component.
 * 
 * Displays content meant for a Bootstrap modal to recover a user's account through their email.
 */
@Component({
  selector: 'app-forgotpass',
  templateUrl: './forgotpass.component.html',
  styleUrls: ['./forgotpass.component.css']
})
export class ForgotpassComponent implements OnInit {

  /**
   * forgot password modal reference
   */
  modal: NgbActiveModal;

  /**
   * email input icon
   */
  emailIcon = faEnvelope;

  /**
   * email value from form
   */
  emailValue: string = '';
  /**
   * flag to check form submission status
   */
  submitted = false;
  /**
   * form reference to recover a user account
   */
  resetForm!: FormGroup;

  /**
   * Constructor for the forgot password component.
   * Initializes the forgot password modal reference from Bootstrap Active Modal.
   * @param modal active modal from Bootstrap
   * @param authServ authentication service
   */
  constructor(modal: NgbActiveModal, private authServ: AuthService) {
    this.modal = modal;
  }

  /**
   * Initializes the form to recover a user's account with necessary controls and validators.
   */
  ngOnInit(): void {
    this.resetForm = new FormGroup({
      email: new FormControl(this.emailValue, [
        Validators.required,
        Validators.email,
        Validators.maxLength(254)
      ])
    });
  }

  /**
   * Method called upon form submission.
   * 
   * Checks whether form is valid, gets the email and calls the method to send an email to the user.
   */
  onSubmit() {
    if (this.resetForm.valid) {
      this.submitted = true;
      // get form values
      this.emailValue = this.resetForm.get('email')?.value;
      // send reset email
      this.resetPassword(this.emailValue);
    }
  }

  /**
   * Sends a password reset email using the authentication service.
   * @param email user email account to send the email to
   */
  resetPassword(email: string) {
    this.authServ.resetPassword(email).subscribe((result: any) => { this.modal.close(); }, error => { });
  }
}
