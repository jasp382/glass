import { Component } from '@angular/core';
import { AnimationOptions } from 'ngx-lottie';


/**
 * Not found component. 
 * 
 * Displays content for when the user navigates to a route not included in the app.
 */
@Component({
  selector: 'app-notfound',
  templateUrl: './notfound.component.html',
  styleUrls: ['./notfound.component.css']
})
export class NotfoundComponent {

  /**
   * File path for Lottie animation shown in page
   */
  options: AnimationOptions = { path: './assets/lottie/forest_search.json' };

}
