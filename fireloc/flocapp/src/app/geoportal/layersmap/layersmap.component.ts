import { Component, OnInit } from '@angular/core';

// Font Awesome
import { faPlus, faMinus } from '@fortawesome/free-solid-svg-icons';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as leafSelector from '../../stores/leaf/leaf.reducer';

// Interfaces
import { MappingLayer } from 'src/app/interfaces/maps';


/**
 * Map Layers component.
 * 
 * Displays a list of FireLoc geospatial layers. Possible to get layers with or without authentication.
 */
@Component({
  selector: 'app-layersmap',
  templateUrl: './layersmap.component.html',
  styleUrls: ['./layersmap.component.css']
})
export class LayersmapComponent implements OnInit {

  // icons
  /**
   * icon for openning a layer category
   */
  plusIcon = faPlus;
  /**
   * icon for closing a layer category
   */
  minusIcon = faMinus;

  /**
   * list of geospatial layers
   */

  mapLayers: MappingLayer[] = [];

  ctbOpen: boolean     = true;
  ctbIsActive: boolean = false;

  flocOpen: boolean = true;
  flocIsActive: boolean = false;

  /**
   * Constructor for the Geoportal layers component. Initializes the user logged status.
   * @param store. App Store.
   */
  constructor(
    private store: Store<AppState>
  ) { }

  ngOnInit(): void {
    // Update Map contents list
    this.store
      .select(leafSelector.getMapLayers)
      .subscribe((layers: MappingLayer[]) => {
        this.mapLayers = layers;
      });
    
    // Check Main Contribution Layer active state
    /*this.store
      .select(ctbLyrSelector.ctbIsActive)
      .subscribe((isActive: boolean) => {
        this.ctbIsActive = isActive;
      });
    
    // Check Main Fireloc Layer active state
    this.store
      .select(flocLyrSelector.flocIsActive)
      .subscribe((isActive: boolean) => {
        this.flocIsActive = isActive;
      })*/
  }

  openClose() {};

  activeCtbLayer() {
    //this.store.dispatch(ctbLyrActions.LayerActivation({payload: this.ctbIsActive}));
  };

  activeFlocLayer() {
    //this.store.dispatch(flocLyrActions.FlocLayerActivation({payload: this.flocIsActive}));
  }

}
