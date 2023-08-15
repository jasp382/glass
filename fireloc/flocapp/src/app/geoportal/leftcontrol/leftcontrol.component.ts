import { Component } from '@angular/core';

/**
 * Geoportal Left menu component.
 * 
 * Displays the left menu in the Geoportal. 
 * Hosts the content for Geoportal Layers and Geoportal Legend components.
 */
@Component({
  selector: 'app-leftcontrol',
  templateUrl: './leftcontrol.component.html',
  styleUrls: ['./leftcontrol.component.css']
})
export class LeftcontrolComponent {

  /**
   * active tab in the left menu
   */
  activeTab: number = 1;

  /**
   * Empty constructor.
   */
  constructor() { }

  /**
   * Empty method.
   */
  ngOnInit(): void { }

}
