import { Component, OnInit } from '@angular/core';

// Constant
import { legend } from 'src/app/constants/geoportalLegend';

/**
 * Geoportal Legend component.
 * 
 * Displays a list of FireLoc geospatial layers legend. Component is incomplete due to API unavailability.
 */
@Component({
  selector: 'app-legend',
  templateUrl: './legend.component.html',
  styleUrls: ['./legend.component.css']
})
export class LegendComponent implements OnInit {

  /**
   * list of legend items
   * 
   * INCOMPLETE DUE TO API UNAVAILABILITY.
   */
  legendItems: any[] = legend;

  /**
   * Empty constructor.
   */
  constructor() { }

  /**
   * Empty method.
   */
  ngOnInit(): void { }

}
