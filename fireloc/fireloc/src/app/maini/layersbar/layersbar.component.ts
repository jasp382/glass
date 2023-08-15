import { Component, OnDestroy, OnInit } from '@angular/core';

// Font Awesome
import { faPlus, faMinus } from '@fortawesome/free-solid-svg-icons';

// Interfaces
import { Layer } from 'src/app/interfaces/layers';
import { LayerActions } from 'src/app/redux/actions/layerActions';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';
import { LayerService } from 'src/app/serv/rest/geo/layer.service';

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
export class LayersbarComponent implements OnInit, OnDestroy {

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

  /**
   * Constructor for the Geoportal layers component. Initializes the user logged status.
   * @param authServ authentication service. See {@link AuthService}.
   * @param layerServ layers service. See {@link LayerService}.
   * @param layerActions layers actions. See {@link LayerActions}.
   */
  constructor(
    private authServ: AuthService,
    private layerServ: LayerService,
    private layerActions: LayerActions,
  ) { this.isLoggedIn = this.authServ.isLoggedIn(); }

  /**
   * Gets FireLoc geospatial layers according to user logged status
   */
  ngOnInit(): void { this.isLoggedIn ? this.getLayersToken() : this.getLayersNoToken(); }

  /**
   * Clears layers from Redux
   */
  ngOnDestroy(): void { this.layerActions.clearLayers(); }

  /**
   * Gets layers from API without an authentication token. Uses the layers service, see {@link LayerService} for more information.
   */
  getLayersNoToken() {
    this.layerServ.getLayersNoToken().subscribe((result: any) => { this.getLayersInformation(result.data); }, error => { });
  }

  /**
   * Gets layers from API with an authentication token. Uses the layers service, see {@link LayerService} for more information.
   */
  getLayersToken() {
    this.layerServ.getLayersToken().subscribe((result: any) => { this.getLayersInformation(result.data); }, error => { });
  }

  /**
   * Gets layers information from API results
   * @param APILayers list of layers from the API result
   */
  getLayersInformation(APILayers: any) {
    for (let l of APILayers) {
      // create layer object
      let layer: Layer = {
        id: l.id,
        slug: l.slug,
        level: l.level,
        title: l.designation,
        serverLayer: l.gsrvlyr,
        store: l.store,
        style: l.style,
        workspace: l.workspace,
        isOpen: false,
        child: this.getLayerChildren(l.child)
      }
      // add layer to categories
      this.categories.push(layer);
    }
  }

  /**
   * Gets layer children related to a parent category
   * @param data parent category
   * @returns list of children or null if there are no children
   */
  getLayerChildren(data: any): Layer[] | null {
    // if no children, return null
    if (data === null) return null;

    let children: Layer[] = [];
    for (let child of data) {
      // create layer object
      let layer: Layer = {
        id: child.id,
        level: child.level,
        title: child.designation,
        serverLayer: child.gsrvlyr,
        slug: child.slug,
        store: child.store,
        style: child.style,
        workspace: child.workspace,
        isOpen: false,
        canOpen: child.child === null ? false : true,
        child: this.getLayerChildren(child.child)
      }
      // add layer to children array
      children.push(layer);
    }
    // return children array
    return children;
  }

  /**
   * Opens or closes a geospatial layer category
   * @param category category to open or close
   */
  toggleCategory(category: Layer) {
    category.isOpen = !category.isOpen;

    // if category is now closed, remove layers from redux
    if (!category.isOpen) {
      this.removeChildLayersFromRedux(category.child);
    }
  }

  /**
   * Removes child layers from Redux if parent category is closed
   * @param children category child layers
   * @returns nothing
   */
  removeChildLayersFromRedux(children: any) {
    // base case: do nothing if there are no more children
    if (children === null) return;

    for (let child of children) {
      this.layerActions.removeLayer(child);
      this.removeChildLayersFromRedux(child.child);
    }
  }

  /**
   * Add or remove layers in Redux.
   * 
   * INCOMPLETE METHOD DUE TO API UNAVAILABILITY.
   * @param event selection event from checkbox input
   * @param layer geospatial layer
   */
  onChangeLayers(event: any, layer: Layer) {
    // Add layer to redux
    if (event.target.checked) this.layerActions.addLayer(layer);
    // Remove layer from redux
    else this.layerActions.removeLayer(layer);
  }

}
