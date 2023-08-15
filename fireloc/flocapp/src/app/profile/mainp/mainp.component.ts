import { Component, OnInit } from '@angular/core';

// Routing
import { Router } from '@angular/router';

// Style
import { faAsterisk, faUser, faList, faTimes } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-mainp',
  templateUrl: './mainp.component.html',
  styleUrls: ['./mainp.component.css']
})
export class MainpComponent implements OnInit {

  /**
   * current active tab in the profile
   */
  activeTab: number = 1;

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

  constructor(private router: Router) {}

  ngOnInit(): void {
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
      //this.getUserContribs();
      this.activeTab = 1;
    }
  }

  /**
   * Changes URL on tab click
   * @param path 
   */
  navigate(path: string) { this.router.navigate([path]); }

}
