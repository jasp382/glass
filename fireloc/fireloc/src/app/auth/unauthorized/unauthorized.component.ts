import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';

// redux
import { select } from '@angular-redux/store';
import { selectLanguage } from 'src/app/redux/selectors';

/**
 * Unauthorized component.
 * 
 * Displays content for when the user navigates to a route and does not have permission to view the content.
 */
@Component({
  selector: 'app-unauthorized',
  templateUrl: './unauthorized.component.html',
  styleUrls: ['./unauthorized.component.css']
})
export class UnauthorizedComponent implements OnInit {

  /**
   * current app language
   */
  language: string = 'pt';
  /**
   * Redux subscription to receive app language updates
   */
  @select(selectLanguage) language$!: Observable<boolean>;

  /**
   * Empty constructor
   */
  constructor() { }

  /**
   * Calls the method to subscribe to redux updates
   */
  ngOnInit(): void { this.subscribeToRedux(); }

  /**
   * Subscribe to redux updates about app language changes
   */
  subscribeToRedux() {
    // update the language used in the app
    this.language$.subscribe((language: any) => { this.language = language; });
  }

}
