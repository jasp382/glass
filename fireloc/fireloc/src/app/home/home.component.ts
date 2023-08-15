import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

// Style
import { NgbCarouselConfig, NgbModal, NgbAlertConfig } from '@ng-bootstrap/ng-bootstrap';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';

// Constants
import { imageSource } from '../constants/homeImages';

// Components
import { LoginComponent } from '../auth/login/login.component';
import { SignupComponent } from '../auth/signup/signup.component';
import { ResetpassComponent } from '../auth/resetpass/resetpass.component';

// Services
import { AuthService } from '../serv/rest/users/auth.service';

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
export class HomeComponent implements OnInit {

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
    private modalService: NgbModal,
    private route: ActivatedRoute,
    private authServ: AuthService,
  ) {
    // customize default values of carousel
    config.interval = 5000;
    config.wrap = true;
    config.keyboard = false;
    config.pauseOnHover = false;
    config.showNavigationArrows = false;
    config.showNavigationIndicators = false;

    // check if user is logged in to disable login and register
    this.isLoggedIn = this.authServ.isLoggedIn();
  }

  /**
   * Opens the reset password modal if the current URL has the correct parameters for it
   */
  ngOnInit(): void {
    this.route.queryParamMap
      .subscribe((params) => {
        // if url has a reset and token parameter
        if (params.has('reset') && params.has('t')) {
          // get token value
          let token = params.get('t');
          if (token != null) {
            // open reset password modal
            this.openResetPassword(token);
          }
        }
      });
  }

  /**
   * Opens the login modal if the user is not logged in
   */
  openLogin() {
    this.isLoggedIn = this.authServ.isLoggedIn();
    if (!this.isLoggedIn) this.modalService.open(LoginComponent, { centered: true });
  }

  /**
   * Opens the register modal if the user is not logged in
   */
  openRegister() {
    this.isLoggedIn = this.authServ.isLoggedIn();
    if (!this.isLoggedIn) this.modalService.open(SignupComponent, { centered: true });
  }

  /**
   * Opens the reset password modal
   * @param token token to reset password
   */
  openResetPassword(token: string) {
    this.isLoggedIn = this.authServ.isLoggedIn();
    if (!this.isLoggedIn) {
      const modalRef = this.modalService.open(ResetpassComponent, { centered: true });
      modalRef.componentInstance.token = token;
    }
  }

}
