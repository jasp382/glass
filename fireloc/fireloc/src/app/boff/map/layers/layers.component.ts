import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

// Fort Awesome
import {
  faChevronDown,
  faChevronUp,
  faPencilAlt,
  faPlus,
  faSearch,
  faTimes,
  faTrash
} from '@fortawesome/free-solid-svg-icons';

// Bootstrap
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FirelocLayer } from 'src/app/interfaces/layers';

// Services
import { LayerService } from 'src/app/serv/rest/geo/layer.service';

/**
 * Backoffice Layers component.
 * 
 * Displays a list of FireLoc geospatial layers and their respective categories. 
 * A single layer can be created, viewed, edited or deleted.
 * It is also possible to filter the layers list with search terms.
 */
@Component({
  selector: 'boff-layers',
  templateUrl: './layers.component.html',
  styleUrls: ['./layers.component.css']
})
export class LayersComponent implements OnInit {

  // icons
  /**
   * icon for adding a new layer
   */
  plusIcon = faPlus;
  /**
   * icon to open a category
   */
  dropIcon = faChevronDown;
  /**
   * icon to close a category
   */
  upIcon = faChevronUp;
  /**
   * icon for search input
   */
  searchIcon = faSearch;
  /**
   * icon to edit a layer
   */
  editIcon = faPencilAlt;
  /**
   * icon to delete a layer
   */
  deleteIcon = faTrash;
  /**
   * icon to close information
   */
  closeIcon = faTimes;

  // table
  /**
   * list of FireLoc geospatial layers
   */
  layers: FirelocLayer[] = [];
  /**
   * list of filtered FireLoc geospatial layers
   */
  filteredLayers: any[] = this.layers;

  // layer details
  /**
   * flag to determine if a single geospatial layer information is being displayed
   */
  isLayerOpen: boolean = false;
  /**
   * single geospatial layer information being displayed
   */
  openLayer!: FirelocLayer;

  /**
   * new category information
   */
  newCategory: any = {
    hasParent: false,
    parent: {},
    catSlug: '',
    catDesignation: '',
    catLevel: 0,
    layerSlug: '',
    layerDesignaton: '',
    layerWorkspace: '',
    layerStore: '',
    layerServerLayer: '',
    layerStyle: '',
  }
  /**
   * new category form reference
   */
  newCategoryForm!: FormGroup;

  /**
   * list of all available geospatial categories
   */
  categories: any[] = [];

  /**
   * new layer information
   */
  newLayer: any = {
    category: {},
    slug: '',
    designation: '',
    workspace: '',
    store: '',
    serverLayer: '',
    style: '',
    child: null,
  };
  /**
   * new layer form reference
   */
  newLayerForm!: FormGroup;

  // edit category and layer
  /**
   * reference to edit category form
   */
  editCategoryForm!: FormGroup;
  /**
   * reference to edit layer form
   */
  editLayerForm!: FormGroup;
  /**
   * reference for the original slug of the opened layer
   */
  openLayerSlug: string = '';

  // remove category and layers
  /**
   * flag to determine if user has confirmed the removal of a layer
   */
  isConfChecked: boolean = false;
  /**
   * flag to determine if user has chosen to delete a layer
   */
  hasClickedRemove: boolean = false;

  /**
   * Empty constructor for Backoffice layers component.
   * @param modalService Bootstrap modal service
   * @param layerServ layers service. See {@link LayerService}.
   */
  constructor(private modalService: NgbModal, private layerServ: LayerService) { }

  /**
   * Initializes data and necessary forms to view, create, update, and delete information.
   */
  ngOnInit(): void {
    // get data
    this.getLayers();

    // new data forms
    this.newCategoryForm = new FormGroup({
      // parent category (optional)
      hasParent: new FormControl(this.newCategory.hasParent),
      parentCategory: new FormControl(this.newCategory.parent),
      // new category
      catDesignation: new FormControl(this.newCategory.catName, [Validators.required, Validators.maxLength(250)]),
      catSlug: new FormControl(this.newCategory.catSlug, [Validators.required, Validators.maxLength(15)]),
      // new layer child for category
      layerDesignation: new FormControl(this.newCategory.layerName, [Validators.required, Validators.maxLength(250)]),
      layerSlug: new FormControl(this.newCategory.layerSlug, [Validators.required, Validators.maxLength(15)]),
      layerWorkspace: new FormControl(this.newCategory.layerWorkspace, [Validators.required, Validators.maxLength(20)]),
      layerStore: new FormControl(this.newCategory.layerStore, [Validators.required, Validators.maxLength(20)]),
      layerServerLayer: new FormControl(this.newCategory.layerServerLayer, [Validators.required, Validators.maxLength(40)]),
      layerStyle: new FormControl(this.newCategory.layerStyle, [Validators.required, Validators.maxLength(20)]),
    });
    this.newLayerForm = new FormGroup({
      category: new FormControl(this.newLayer.category, [Validators.required]),
      slug: new FormControl(this.newLayer.slug, [Validators.required, Validators.maxLength(15)]),
      designation: new FormControl(this.newLayer.name, [Validators.required, Validators.maxLength(250)]),
      workspace: new FormControl(this.newLayer.workspace, [Validators.required, Validators.maxLength(20)]),
      store: new FormControl(this.newLayer.store, [Validators.required, Validators.maxLength(20)]),
      serverLayer: new FormControl(this.newLayer.serverLayer, [Validators.required, Validators.maxLength(40)]),
      style: new FormControl(this.newLayer.style, [Validators.required, Validators.maxLength(20)]),
    });

    // edit data forms
    this.editCategoryForm = new FormGroup({
      designation: new FormControl('', [Validators.required, Validators.maxLength(250)]),
      slug: new FormControl('', [Validators.required, Validators.maxLength(15)]),
    });
    this.editLayerForm = new FormGroup({
      designation: new FormControl('', [Validators.required, Validators.maxLength(250)]),
      slug: new FormControl('', [Validators.required, Validators.maxLength(15)]),
      workspace: new FormControl('', [Validators.required, Validators.maxLength(20)]),
      store: new FormControl('', [Validators.required, Validators.maxLength(20)]),
      serverLayer: new FormControl('', [Validators.required, Validators.maxLength(40)]),
      style: new FormControl('', [Validators.required, Validators.maxLength(20)]),
    });
  }

  /**
   * Gets FireLoc geospatial layers from API.
   */
  getLayers() {
    this.layerServ.getLayersToken(true).subscribe((result: any) => { this.getLayersInformation(result.data); }, error => { });
  }

  /**
   * Gets layer information from API results
   * @param APILayers API response data
   */
  getLayersInformation(APILayers: any) {
    for (let l of APILayers) {
      // create layer object
      let layer: FirelocLayer = {
        id: l.id,
        slug: l.slug,
        level: l.level,
        rootID: l.rootid,
        designation: l.designation,
        serverLayer: l.gsrvlyr,
        store: l.store,
        style: l.style,
        workspace: l.workspace,
        isOpen: false,
        child: this.getLayerChildren(l.child)
      }
      // add layer to categories
      this.layers.push(layer);
    }
  }

  /**
   * Gets layer 'children' from a 'parent' category
   * @param data parent layer
   * @returns list of 'children' or null if there are none
   */
  getLayerChildren(data: any): FirelocLayer[] | null {
    // if no children, return null
    if (data === null) return null;

    let children: FirelocLayer[] = [];
    for (let child of data) {
      // create layer object
      let layer: FirelocLayer = {
        id: child.id,
        slug: child.slug,
        level: child.level,
        rootID: child.rootid,
        designation: child.designation,
        serverLayer: child.gsrvlyr,
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
   * Search geospatial layers by name
   * @param searchTerms 
   * @returns 
   */
  searchLayers(searchTerms: string) {
    // ignore clear search event
    if (typeof (searchTerms) === 'string') {
      this.filteredLayers = JSON.parse(JSON.stringify(this.layers));

      // no search has all layers
      if (searchTerms.length === 0) return;

      // search first categories by name
      else this.filteredLayers = this.recursiveFilter(this.filteredLayers, searchTerms);
    }
  }

  /**
   * Recursively searches child layers
   * @param items layers to search
   * @param search search terms
   * @returns filtered layers
   */
  recursiveFilter(items: any, search: string) {
    return items.filter((item: any) => {
      if (item.child) item.child = this.recursiveFilter(item.child, search);
      return item.designation?.toLowerCase().includes(search) || item.child?.length;
    });
  }

  // expand/collapse table rows
  /**
   * Expands or collapses table rows to display or hide layers from a parent category.
   * @param layerID selected table row ID
   * @param event click event
   * @returns nothing
   */
  toggleCategory(layerID: number, event: any) {
    // if row click was on an action icon, ignore row select
    if (event.path !== undefined && (event.path[1].id === 'editIcon' || event.path[2].id === 'editIcon')) return;

    // mutate data array 
    JSON.stringify(this.filteredLayers, (_, nestedLayer) => {
      if (nestedLayer && nestedLayer.id === layerID && nestedLayer.child !== null) {
        // toggle layer expansion
        nestedLayer.isOpen = !nestedLayer.isOpen;

        // if parent is now closed, close descendants
        if (!nestedLayer.isOpen && nestedLayer.child !== null) this.closeChildren(nestedLayer);
      }
      return nestedLayer;
    });
  }

  /**
   * Closes the display of all layers below a chosen layer
   * @param layerObject layer category to close
   * @returns nothing
   */
  closeChildren(layerObject: any) {
    // base case
    if (layerObject.child === null) return;

    // close children
    layerObject.child.forEach((child: any) => {
      child.isOpen = false;
      this.closeChildren(child);
    })
  }

  /**
   * Opens the Bootstrap modal to create a new layer.
   * @param content modal content to display
   */
  openCreateModal(content: any) {
    // get list of all categories
    this.categories = [];
    this.layers.forEach((l: any) => this.getAllCategories(l));

    // update new layer information
    this.newLayer.category = this.categories[0];
    this.newLayerForm.patchValue({ category: this.newLayer.category });

    // update new category information
    this.newCategory.parent = this.categories[0];
    this.newCategoryForm.patchValue({ parentCategory: this.newCategory.parent })

    // open edit modal
    this.modalService.open(content, { centered: true, size: 'lg' });
  }

  /**
   * Gets all available categories. Needed for the new layer form.
   * @param layerObj parent category
   * @returns nothing
   */
  getAllCategories(layerObj: any) {
    // base case
    if (layerObj.child === null) return

    // add category
    this.categories.push(layerObj);
    layerObj.child.forEach((l: any) => this.getAllCategories(l));
  }

  /**
   * Updates new category information from input form
   * @param value updated value
   * @param field object property to update
   */
  updateNewCategoryField(value: string | number | boolean, field: string) { this.newCategory[field] = value; }

  /**
   * Updates new layer information from input form
   * @param value updated value
   * @param field object property to update
   */
  updateNewLayerField(value: string | number, field: string) { this.newLayer[field] = value; }

  /**
   * Finds a layer and appends a 'child' to it.
   * @param layerObj layer being searched
   * @param parent parent to find
   * @param newChild child to append
   * @returns nothing
   */
  findLayerAndAddChild(layerObj: any, parent: any, newChild: any) {
    // base case
    if (layerObj.child === null) return;

    // if parent is found, add child to end of array
    if (layerObj.id === parent.id) {
      layerObj.child.push(newChild);
    }

    // continue search if not found
    for (let c of layerObj.child) {
      if (c.child !== null) this.findLayerAndAddChild(c, parent, newChild);
    }
  }

  /**
   * Creates a new category with the API if the new category form is valid.
   * For a category to be valid, it needs to have a child and therefore upon successful category creation a child layer is created and appended to it.
   */
  createCategory() {
    // check if form is valid
    if (this.newCategoryForm.valid) {
      let data = [{
        // category
        slug: this.newCategory.catSlug,
        designation: this.newCategory.catDesignation,
        level: 1,
      }, {
        // layer
        slug: this.newCategory.layerSlug,
        designation: this.newCategory.layerDesignation,
        level: 2,
        rootid: this.newCategory.catSlug,
        workspace: this.newCategory.layerWorkspace,
        store: this.newCategory.layerStore,
        gsrvlyr: this.newCategory.layerServerLayer,
        style: this.newCategory.layerStyle,
      }];

      let hasParent = this.newCategory.hasParent;
      let catParent = this.newCategory.parent;

      // check if new category has parent
      if (hasParent) {
        // get parent information
        let rootID = this.newCategory.parent.slug;
        let catLevel = this.newCategory.parent.level;

        // update data information
        data[0].rootid = rootID;
        data[0].level = catLevel + 1;
        data[1].level = catLevel + 2;
      }

      // add category with API
      this.layerServ.createLayer(data[0]).subscribe(
        (result: any) => {
          // get created category
          let newCategory: FirelocLayer = {
            id: result.id,
            slug: result.slug,
            level: result.level,
            rootID: result.rootid,
            designation: result.designation,
            serverLayer: result.gsrvlyr,
            store: result.store,
            style: result.style,
            workspace: result.workspace,
            child: [],
            canOpen: true,
            isOpen: false,
          }

          // add child layer with API
          this.layerServ.createLayer(data[1]).subscribe(
            (result: any) => {
              // get created child for category
              let newChild: FirelocLayer = {
                id: result.id,
                slug: result.slug,
                level: result.level,
                rootID: result.rootid,
                designation: result.designation,
                serverLayer: result.gsrvlyr,
                store: result.store,
                style: result.style,
                workspace: result.workspace,
                child: null,
                canOpen: false,
                isOpen: false,
              }

              // add child to category
              newCategory.child?.push(newChild);

              // if category does not have a parent category, just add it to table
              if (!hasParent) this.layers.push(newCategory);
              // find parent in table and add category
              else {
                for (let i = 0; i < this.layers.length; i++) {
                  // if parent is main category, add to table
                  if (this.layers[i].id === catParent.id) {
                    this.layers[i].child?.push(newCategory);
                  }
                  else {
                    this.findLayerAndAddChild(this.layers[i], catParent, newCategory);
                  }
                }
              }
            }, error => { }
          );
        }, error => { }
      );
    }

    // close and reset
    this.newCategoryForm.reset();
    this.modalService.dismissAll();
  }

  /**
   * Creates a new geospatial layer with the API if the new layer form is valid.
   */
  createLayer() {
    // check if form is valid
    if (this.newLayerForm.valid) {
      // get category information
      let rootID = this.newLayer.category.slug;
      let catLevel = this.newLayer.category.level;

      // prepare API request data
      let data = {
        slug: this.newLayer.slug,
        designation: this.newLayer.designation,
        level: catLevel + 1,
        rootid: rootID,
        workspace: this.newLayer.workspace,
        store: this.newLayer.store,
        gsrvlyr: this.newLayer.serverLayer,
        style: this.newLayer.style,
      }

      // add layer with API
      this.layerServ.createLayer(data).subscribe(
        (result: any) => {
          // get created layer
          let newChild: FirelocLayer = {
            id: result.id,
            slug: result.slug,
            level: result.level,
            rootID: result.rootid,
            designation: result.designation,
            serverLayer: result.gsrvlyr,
            store: result.store,
            style: result.style,
            workspace: result.workspace,
            child: null,
          }

          // find parent category and add layer to child array for display
          for (let i = 0; i < this.layers.length; i++) {
            // if parent layer is a main category, add child to it
            if (this.layers[i].id === this.newLayer.category.id)
              this.layers[i].child?.push(newChild);
            else
              this.findLayerAndAddChild(this.layers[i], this.newLayer.category, newChild);
          }
        }, error => { }
      );
    }

    // close and reset
    this.newLayerForm.reset();
    this.modalService.dismissAll();
  }

  /**
   * Opens the Bootstrap modal to edit a layers information
   * @param layerObj layer information to edit
   * @param content modal content
   */
  openEditModal(layerObj: FirelocLayer, content: any) {
    // update edit form values
    this.openLayer = { ...layerObj };
    this.openLayerSlug = layerObj.slug;
    if (layerObj.child)
      this.editCategoryForm.setValue({
        designation: this.openLayer.designation,
        slug: this.openLayer.slug,
      });
    else
      this.editLayerForm.setValue({
        designation: this.openLayer.designation,
        slug: this.openLayer.slug,
        workspace: this.openLayer.workspace,
        store: this.openLayer.store,
        serverLayer: this.openLayer.serverLayer,
        style: this.openLayer.style,
      });

    // open edit modal
    this.modalService.open(content, { centered: true });
  }

  /**
   * Updates layer information from edit input form
   * @param value updated value
   * @param field object property to update
   */
  updateEditLayerField<K extends keyof FirelocLayer>(value: FirelocLayer[K], field: K) { this.openLayer[field] = value; }

  /**
   * Updates category with the API, if the edit category form is valid
   */
  updateCategory() {
    // check if form is valid
    if (this.editCategoryForm.valid) {
      let requestData: any = {};

      // add changed values to request data
      Object.keys(this.editCategoryForm.controls).forEach((key: string) => {
        // if input changed, add to request data
        if (this.editCategoryForm.get(key)?.dirty) {
          switch (key) {
            case 'designation': requestData.designation = this.openLayer.designation; break;
            case 'slug': requestData.slug = this.openLayer.slug; break;
          }
        }
      });

      // send API request
      this.layerServ.updateLayer(this.openLayerSlug, requestData).subscribe(
        (result: any) => {
          // get updated layer
          let updatedLayer: FirelocLayer = {
            id: result.id,
            slug: result.slug,
            level: result.level,
            rootID: result.rootid,
            designation: result.designation,
            serverLayer: this.openLayer.serverLayer,
            store: this.openLayer.store,
            style: this.openLayer.style,
            workspace: this.openLayer.workspace,
            child: this.openLayer.child,
            isOpen: this.openLayer.isOpen,
            canOpen: this.openLayer.canOpen,
          };

          // find layer and update table data
          let finalResult = this.layers.map((layer) => this.findLayerAndUpdate(layer, updatedLayer));
          this.layers = finalResult;
        }, error => { }
      );
    }

    // close and reset
    this.editCategoryForm.reset();
    this.modalService.dismissAll();
  }

  /**
   * Updates a geospatial layer with the API, if the edit layer form is valid.
   */
  updateLayer() {
    // check if form is valid
    if (this.editLayerForm.valid) {
      let requestData: any = {};

      // add changed values to request data
      Object.keys(this.editLayerForm.controls).forEach((key: string) => {
        // if input changed, add to request data
        if (this.editLayerForm.get(key)?.dirty) {
          switch (key) {
            case 'designation': requestData.designation = this.openLayer.designation; break;
            case 'slug': requestData.slug = this.openLayer.slug; break;
            case 'workspace': requestData.workspace = this.openLayer.workspace; break;
            case 'store': requestData.store = this.openLayer.store; break;
            case 'serverLayer': requestData.layer = this.openLayer.serverLayer; break;
            case 'style': requestData.style = this.openLayer.style; break;
          }
        }
      });

      this.layerServ.updateLayer(this.openLayerSlug, requestData).subscribe(
        (result: any) => {
          // get updated layer
          let updatedLayer: FirelocLayer = {
            id: result.id,
            slug: result.slug,
            level: result.level,
            rootID: result.rootid,
            designation: result.designation,
            serverLayer: result.gsrvlyr,
            store: result.store,
            style: result.style,
            workspace: result.workspace,
            child: null,
            isOpen: false,
            canOpen: false,
          };

          // find layer and update table data
          let finalResult = this.layers.map((layer) => this.findLayerAndUpdate(layer, updatedLayer));
          this.layers = finalResult;
        }, error => { }
      );
    }

    // close and reset
    this.editLayerForm.reset();
    this.modalService.dismissAll();
  }

  /**
   * Finds a layer in a nested list and updates its information.
   * @param layerObj layer being searched
   * @param updatedLayer updated layer
   * @returns updated layer
   */
  findLayerAndUpdate(layerObj: FirelocLayer, updatedLayer: any): FirelocLayer {
    // base case
    if (layerObj === null) return layerObj;

    // if layer is found, update data
    if (layerObj.id === updatedLayer.id) {
      layerObj = { ...updatedLayer };
      return layerObj;
    }

    // continue search if not found
    if (layerObj.child) layerObj.child = layerObj.child.map((layer) => this.findLayerAndUpdate(layer, updatedLayer));
    return layerObj;
  }

  /**
   * Opens a Bootstrap modal to delete a layer.
   * @param layerObj layer to remove
   * @param content modal content to display
   */
  openDeleteModal(layerObj: any, content: any) {
    // update open layer values
    this.openLayer = { ...layerObj };

    // reset variables for new modal
    this.isConfChecked = false;
    this.hasClickedRemove = false;

    // open modal
    this.modalService.open(content, { centered: true, size: 'lg' });
  }

  /**
   * Finds a layer and removes its child from its children's list
   * @param layerObj layer being searched
   * @param objID child ID to delete
   * @returns 
   */
  findAndRemoveLayer(layerObj: any, objID: number) {
    // base case
    if (layerObj.child === null) return;

    // if layer has a child with ID, remove child
    for (let i = 0; i < layerObj.child.length; i++) {
      if (layerObj.child[i].id === objID) {
        layerObj.child.splice(i, 1);
        return;
      }
    }

    // continue search if not found
    for (let c of layerObj.child) this.findAndRemoveLayer(c, objID);
  }

  // delete layer/category
  /**
   * Checks if the user has confirmed the removal of a geospatial layer or category.
   * 
   * If there is confirmation, delete a layer/category with the API and update the displayed data.
   */
  removeLayer() {
    this.hasClickedRemove = true;
    // check if user has confirmed
    if (this.isConfChecked) {
      // delete layer with API
      this.layerServ.deleteLayer(this.openLayer.slug).subscribe(
        (result: any) => {
          // remove layer from displayed list
          for (let i = 0; i < this.filteredLayers.length; i++) {
            // if deleted layer is a main category, remove it
            if (this.filteredLayers[i].id === this.openLayer.id)
              this.filteredLayers.splice(i, 1);
            else
              this.findAndRemoveLayer(this.filteredLayers[i], this.openLayer.id);
          }
        }, error => { }
      );

      // close and reset
      this.isConfChecked = false;
      this.hasClickedRemove = false;
      this.modalService.dismissAll();
    }
  }

}
