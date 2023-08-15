import { Component, OnInit } from '@angular/core';

// Font Awesome
import { faPlus, faMinus } from '@fortawesome/free-solid-svg-icons';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as loginSelector from '../../stores/login/login.reducer';
import * as layersSelector from '../../stores/geolyr/geolyr.reducer';
import * as layersActions from '../../stores/geolyr/geolyr.actions';

// Interfaces
import { TreeLayer, Layer } from 'src/app/interfaces/layers';
import { Token } from 'src/app/interfaces/login';

export interface LayersTree {
  isOpen: boolean,
  canOpen: boolean,
  child: LayersTree[]|null
}

/**
 * Geoportal Layers component.
 * 
 * Displays a list of FireLoc geospatial layers. Possible to get layers with or without authentication.
 */
@Component({
  selector: 'app-layersbar',
  templateUrl: './layersbar.component.html',
  styleUrls: ['./layersbar.component.css']
})
export class LayersbarComponent implements OnInit {

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
   * flag to determine user logged status
   */
  isLoggedIn: boolean = false;

  /**
   * list of geospatial layers
   */
  categories: Layer[] = [];

  token: Token|null = null;

  layers: TreeLayer[] = [];
  layersAux: LayersTree[] = [];

  /**
   * Constructor for the Geoportal layers component. Initializes the user logged status.
   * @param authServ authentication service. See {@link AuthService}.
   * @param layerServ layers service. See {@link LayerService}.
   * @param layerActions layers actions. See {@link LayerActions}.
   */
  constructor(
    private store: Store<AppState>,
  ) { }

  ngOnInit(): void {
    // Update Tree Layer State
    this.store
      .select(loginSelector.getLoginToken)
      .subscribe((logState: Token|null) => {
        this.token = logState;

        this.store.dispatch(layersActions.GetTreeLayer(
          {payload: {token: this.token, astree: true} }
        ));
      });
    
    // Login State
    this.store
      .select(loginSelector.getLoginStatus)
      .subscribe((logStatus: boolean) => {
        this.isLoggedIn = logStatus;
      });
    
    // Get Tree Layer current state
    this.store
      .select(layersSelector.getTreeLayer)
      .subscribe((tree: TreeLayer[]) => {
        this.layers = tree;

        for (let l of this.layers) {
          let laux: LayersTree = {
            isOpen: false,
            canOpen: true,
            child: this.getLayerChildren(l.child)
          }

          this.layersAux.push(laux);
        }
      });
  }

  /**
   * Gets layer children related to a parent category
   * @param data parent category
   * @returns list of children or null if there are no children
   */
  getLayerChildren(data: TreeLayer[]|null): LayersTree[]|null {
    // if no children, return null
    if (data === null) return null;

    let children: LayersTree[] = [];
    for (let child of data) {
      let lyr: LayersTree = {
        isOpen: false,
        canOpen: child.child === null ? false : true,
        child: this.getLayerChildren(child.child)
      }

      children.push(lyr);
    }

    return children;
  }

  /**
   * Opens or closes a geospatial layer category
   * @param category category to open or close
   */
  toggleCategory(category: LayersTree) {
    category.isOpen = !category.isOpen;
  }

  /**
   * Add or remove layers
   */
  changeLayers() {}

}
