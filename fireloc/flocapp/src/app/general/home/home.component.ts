import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

// Style
import { NgbCarouselConfig, NgbModal, NgbAlertConfig, NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';

// Constants
import { imageSource } from 'src/app/constants/homeImages';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as fromLoginSelector from '../../stores/login/login.reducer';

import { LoginComponent } from 'src/app/auth/login/login.component';
import { SignupComponent } from 'src/app/auth/signup/signup.component';
import { ResetpassComponent } from 'src/app/auth/resetpass/resetpass.component';

/**
 * App Home component.
 * First component displayed when a user first accesses the application.
 * 
 * Features an image slideshow and multiple action links/buttons to redirect to other locations.
 * Also features a footer with all the envolved parties in the FireLoc system.
 */
@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  providers: [NgbCarouselConfig, NgbAlertConfig]
})
export class HomeComponent {

  /**
   * carousel image sources
   */
  images = imageSource;

  /**
   * arrow icon
   */
  arrowIcon = faAngleRight;

  /**
   * flag to determine the user's logged status
   */
  isLoggedIn: boolean = false;
  
  /**
   * Constructor for the home component. 
   * Initializes the settings for the image carousel and the logged status.
   * @param config Bootstrap carousel configuration
   * @param modalService Bootstrap modal service
   * @param route Angular activated route
   * @param authServ authentication service. See {@link AuthService}.
   */
  constructor(
    config: NgbCarouselConfig,
    private store: Store<AppState>,
    private modalService: NgbModal,
    private route: ActivatedRoute,
    //private authServ: AuthService,
  ) {
    // customize default values of carousel
    config.interval = 5000;
    config.wrap = true;
    config.keyboard = false;
    config.pauseOnHover = false;
    config.showNavigationArrows = false;
    config.showNavigationIndicators = false;
  }

  ngOnInit(): void {
    this.store
      .select(fromLoginSelector.getLoginStatus)
      .subscribe((loginState: boolean) => {
        this.isLoggedIn = loginState;
      })
  }

  /**
   * Opens the login modal if the user is not logged in
   */
  openLogin() {
    if (!this.isLoggedIn) {
      this.modalService.open(LoginComponent, { centered: true});
    }
  }

  /**
   * Opens the register modal if the user is not logged in
   */
  openRegister() {
    if (!this.isLoggedIn) this.modalService.open(SignupComponent, { centered: true });
  }

  /**
   * Opens the reset password modal
   * @param token token to reset password
   */
  openResetPassword(token: string) {
    if (!this.isLoggedIn) {
      const modalRef = this.modalService.open(
        ResetpassComponent, { centered: true }
      );

      modalRef.componentInstance.token = token;
    }
  }

}
