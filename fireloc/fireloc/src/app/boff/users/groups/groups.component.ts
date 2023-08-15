import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

// Style
import { faPlus, faSearch, faTimes } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces
import { TableHeader } from 'src/app/interfaces/backoffice';
import { FirelocLayer } from 'src/app/interfaces/layers';
import { Group } from 'src/app/interfaces/users';

// Services
import { GroupService } from 'src/app/serv/rest/users/group.service';
import { LayerService } from 'src/app/serv/rest/geo/layer.service';

/**
 * Backoffice Groups component.
 * 
 * Displays a list of FireLoc user groups. A single user group can be created, viewed, edited or deleted. 
 * It is also possible to filter the user groups with search terms.
 * 
 * When a user group is selected, a list of associated geospatial layers table is displayed. These layers are the only ones visible to each user group.
 * It is also possible to associate new layers, remove layers associations and search for missing layers.
 */
@Component({
  selector: 'boff-groups',
  templateUrl: './groups.component.html',
  styleUrls: ['./groups.component.css']
})
export class GroupsComponent implements OnInit {

  // icons
  /**
   * icon for group creating or layer association
   */
  plusIcon = faPlus;
  /**
   * icon to close information
   */
  closeIcon = faTimes;
  /**
   * icon for search
   */
  searchIcon = faSearch;

  // groups search
  /**
   * search terms for groups data filtering
   */
  searchTerms: string = '';

  // data
  /**
   * list of all user groups available
   */
  groups: Group[] = [];
  /**
   * list of all geospatial layers available
   */
  layers: FirelocLayer[] = [];

  // groups table
  /**
   * list of table headers for groups table component
   */
  groupHeaders: TableHeader[] = [
    { objProperty: 'id', columnLabel: '#' },
    { objProperty: 'name', columnLabel: 'Grupo' },
  ];
  /**
   * selected group ID
   */
  selectedGroupID: number = -1;

  // layers table
  /**
   * flag to determine if a single group's information is being displayed 
   */
  isGroupOpen: boolean = false;
  /**
   * list of layers associated to a user group
   */
  layersData: FirelocLayer[] = [];
  /**
   * list of table headers for layers table component
   */
  layerHeaders: TableHeader[] = [
    { objProperty: 'id', columnLabel: '#' },
    { objProperty: 'designation', columnLabel: 'Camadas Visíveis' }
  ];

  // group pagination
  /**
   * current page of group data being displayed
   */
  currentGroupPage: number = 1;
  /**
   * number of rows of group data in the groups table
   */
  groupRowCount: number = this.groups.length;

  // layer pagination
  /**
   * current page of layer data being displayed
   */
  currentLayerPage: number = 1;
  /**
   * number of rows of layers data in the layers table
   */
  layerRowCount: number = this.layersData.length;

  // create new group
  /**
   * new user group form
   */
  newGroupForm!: FormGroup;
  /**
   * new user group data
   */
  newGroup = { name: '', }

  // edit group
  /**
   * edit user group form
   */
  editGroupForm!: FormGroup;
  /**
   * reference to open user group for editing
   */
  editGroup!: Group;

  // remove group
  /**
  * flag to determine if user has confirmed user group removal
  */
  isConfChecked: boolean = false;
  /**
   * flag to determine if user has decided to remove a user group
   */
  hasClickedRemove: boolean = false;

  // associate layers  
  /**
   * list of missing layers of a user group
   */
  missingLayers: FirelocLayer[] = [];
  /**
   * list of filters missing layers of a user group
   */
  filteredMissingLayers: FirelocLayer[] = [];
  /**
   * layer search terms
   */
  layerSearch: string = '';

  /**
   * Empty constructor for the Backoffice Groups component.
   * @param modalService Bootstrap modal service
   * @param groupServ group service. See {@link GroupService}.
   * @param layerServ layer service. See {@link LayerService}.
   */
  constructor(private modalService: NgbModal, private groupServ: GroupService, private layerServ: LayerService) { }

  /**
   * Initializes data and necessary forms (create and edit a user group).
   */
  ngOnInit(): void {
    // get data 
    this.getGroups();
    this.getLayers();

    this.newGroupForm = new FormGroup({
      name: new FormControl(this.newGroup.name, [Validators.required, Validators.maxLength(100)]),
    });
    this.editGroupForm = new FormGroup({
      name: new FormControl(this.newGroup.name, [Validators.required, Validators.maxLength(100)]),
    });
  }

  /**
   * Get user groups data from API
   */
  getGroups() {
    this.groupServ.getGroups(false, true).subscribe(
      (result: any) => {
        // add groups
        result.data.forEach((g: any) => {
          // compile group information
          let newGroup: Group = {
            id: g.id,
            name: g.name,
            layers: this.getLayerInfo(g.layers)
          };
          this.groups.push(newGroup);
        });

        // update values for table and pagination
        this.groups = JSON.parse(JSON.stringify(this.groups));
        this.updateGroupRowCount(this.groups.length);
      }, error => { }
    );
  };

  /**
   * Gets geospatial layers from API
   */
  getLayers() {
    this.layerServ.getLayersToken(false).subscribe((result: any) => { this.layers = this.getLayerInfo(result.data); }, error => { });
  }

  /**
   * Gets geospatial layers information from API request response
   * @param layers API response data
   * @returns list of geospatial layers
   */
  getLayerInfo(layers: any[]): FirelocLayer[] {
    let list: FirelocLayer[] = [];
    layers.forEach((l: any) => {
      if (l.gsrvlyr !== null) {
        let newLayer: FirelocLayer = {
          id: l.id,
          designation: l.designation,
          serverLayer: l.gsrvlyr,
          level: l.level,
          rootID: l.rootid,
          slug: l.slug,
          store: l.store,
          style: l.style,
          workspace: l.workspace
        }
        list.push(newLayer);
      }
    });
    return list;
  }

  /**
   * Updates search terms.
   * Searches user groups by name in table component. 
   * See {@link TableComponent#filterDataSearchGroups} for more information.
   * @param searchTerms new search terms
   */
  searchGroups(searchTerms: string) {
    // ignore clear search event
    if (typeof (searchTerms) === 'string') this.searchTerms = searchTerms;
  }

  /**
   * Updates row count of filtered data for group pagination
   * @param rows number of user groups
   */
  updateGroupRowCount(rows: number) { this.groupRowCount = rows; }

  /**
   * Updates current page for groups table
   * @param page current page
   */
  getGroupPage(page: any) { this.currentGroupPage = page; }

  /**
   * Updates current page for layers table
   * @param page current page
   */
  getLayerPage(page: any) { this.currentLayerPage = page; }

  /**
   * Displays or hides geospatial layers list associated to a user group.
   * @param groupID selected user group or -1 to close layers table
   */
  toggleGroupLayers(groupID: number) {
    // close group layers table
    if (groupID === -1) {
      this.isGroupOpen = false;
      this.selectedGroupID = -1;
    }
    // open group layers table
    else {
      this.isGroupOpen = true;
      this.selectedGroupID = groupID;

      // find layers with selected group ID
      let groupIndex = this.groups.findIndex(item => item.id === groupID);
      let group = this.groups[groupIndex];
      if (group.layers !== undefined)
        this.layersData = group.layers;

      // update layers table row count
      this.layerRowCount = this.layersData.length;
    }
  }

  /**
   * Remove layer association from user group with API
   * @param layerID layer ID to remove
   */
  unlinkLayer(layerID: number) {
    // find layer in group
    let groupIndex = this.groups.findIndex(item => item.id === this.selectedGroupID);
    let group = this.groups[groupIndex];
    if (group.layers !== undefined) {
      let layerIndex = group.layers.findIndex((layer: any) => layer.id === layerID);
      let layer = group.layers[layerIndex];
      let slug = [layer.slug];

      this.layerServ.setGroupLayers(group.name, slug, 'delete').subscribe(
        (result: any) => {
          // update layers table and pagination
          if (group.layers !== undefined) {
            group.layers.splice(layerIndex, 1);
            this.layersData = JSON.parse(JSON.stringify(group.layers));
            this.layerRowCount = this.layersData.length;
          }
        }, error => { }
      );
    }
  }

  /**
   * Opens a Bootstrap modal to create, edit or delete a user. Initializes data before opening the modal.
   * @param content modal content to be displayed
   * @param groupID group ID to edit or delete, or -1 to create a new group
   */
  open(content: any, groupID: number) {
    // groupID -1 for new group
    if (groupID !== -1) {
      // reset variables for new modal (edit or delete)
      this.isConfChecked = false;
      this.hasClickedRemove = false;
      this.selectedGroupID = groupID;

      // find group with selected group ID
      let groupIndex = this.groups.findIndex(item => item.id === groupID);

      // update edit group form values
      this.editGroup = { name: this.groups[groupIndex].name, id: groupID };
      this.editGroupForm.setValue({ name: this.editGroup.name, });
    }

    // open modal
    this.modalService.open(content, { centered: true });
  }

  /**
   * Opens Bootstrap modal to associate layers to a user group.
   * @param content modal content to be displayed
   */
  openLayerModal(content: any) {
    // find group with selected group ID
    let groupIndex = this.groups.findIndex(item => item.id === this.selectedGroupID);
    this.missingLayers = JSON.parse(JSON.stringify(this.layers));

    // populate missing layers array with layers missing from group
    this.missingLayers = this.missingLayers.filter(layer =>
      !this.groups[groupIndex].layers?.filter((item: any) => item.id === layer.id).length
    );

    // copy missing layers to filtered for search
    this.filteredMissingLayers = JSON.parse(JSON.stringify(this.missingLayers));

    // open modal
    this.modalService.open(content, { centered: true });
  }

  /**
   * Updates new group information from create input form
   * @param value new group name
   */
  updateNewGroupName(value: string) { this.newGroup.name = value; }

  /**
   * Updates new group information from edit input form
   * @param value updated group name
   */
  updateEditGroupName(value: string) { this.editGroup.name = value; }

  /**
   * Creates a new user group with the API if new group form is valid.
   */
  createNewGroup() {
    // check if form is valid
    if (this.newGroupForm.valid) {
      this.groupServ.addGroup(this.newGroup.name).subscribe(
        (result: any) => {
          // add new group to list
          let groupAdded: Group = {
            id: result.id,
            name: result.name
          };
          this.groups.push(groupAdded);

          // update groups table and pagination
          this.groups = JSON.parse(JSON.stringify(this.groups));
          this.updateGroupRowCount(this.groups.length);
        }, error => { }
      );
      // close and reset
      this.newGroupForm.reset();
      this.modalService.dismissAll();
    }
  }

  /**
   * Updates a user group if edit group form is valid.
   */
  updateGroup() {
    // check if form is valid
    if (this.editGroupForm.valid) {
      // find old group name
      let groupIndex = this.groups.findIndex(item => item.id === this.editGroup.id);
      let group = this.groups[groupIndex];
      let oldName = group.name;

      this.groupServ.updateGroup(oldName, this.editGroup.name).subscribe(
        (result: any) => {
          // update group information and table
          group.name = result.name;
          this.groups = JSON.parse(JSON.stringify(this.groups));
        }, error => { }
      );

      // close and reset
      this.editGroupForm.reset();
      this.modalService.dismissAll();
    }
  }

  /**
   * Checks if the user has confirmed the removal of a user group.
   * 
   * If there is confirmation, delete a user group with the API and update the displayed data.
   */
  deleteGroup() {
    this.hasClickedRemove = true;
    // only delete if user has confirmed decision
    if (this.isConfChecked) {
      // find group name
      let groupIndex = this.groups.findIndex(item => item.id === this.editGroup.id);
      let groupName = this.groups[groupIndex].name;

      // delete group
      this.groupServ.deleteGroup(groupName).subscribe(
        (result: any) => {
          // remove group from list
          this.groups.splice(groupIndex, 1);
          // update groups table and pagination
          this.groups = JSON.parse(JSON.stringify(this.groups));
          this.updateGroupRowCount(this.groups.length);
        }, error => { }
      );

      // close and reset
      this.isGroupOpen = false;
      this.selectedGroupID = -1;
      this.isConfChecked = false;
      this.hasClickedRemove = false;
      this.modalService.dismissAll();
    }
  }

  /**
   * Searches for missing layers in open user group when layer association modal is opened.
   * Searches layers by name
   * @param layerSearch search terms
   */
  searchLayers(layerSearch: string) {
    this.layerSearch = layerSearch;

    // if search is clear, show all missing layers
    if (this.layerSearch.length === 0)
      this.filteredMissingLayers = JSON.parse(JSON.stringify(this.missingLayers));
    else
      this.filteredMissingLayers = this.filteredMissingLayers.filter(layer =>
        layer.designation.toLowerCase().includes(this.layerSearch.toLowerCase())
      );
  }

  /**
   * Selects layer to associate to a user group.
   * @param layer selected layer
   */
  selectLayer(layer: any) {
    let layerIndex = this.missingLayers.findIndex(item => item.id === layer.id);
    this.missingLayers[layerIndex].selected = !this.missingLayers[layerIndex].selected;
  }

  /**
   * Associates layers to a user group with the API
   */
  associateLayers() {
    let groupIndex = this.groups.findIndex(item => item.id === this.selectedGroupID);
    let group = this.groups[groupIndex];

    // get layers slugs
    let slugs: string[] = [];
    group.layers?.forEach(l => slugs.push(l.slug));
    this.missingLayers.forEach(mL => { if (mL.selected) slugs.push(mL.slug); })

    this.layerServ.setGroupLayers(group.name, slugs, 'add').subscribe(
      (result: any) => {
        // update group layers information
        this.missingLayers.forEach(layer => { if (layer.selected) group.layers?.push(layer) });

        // update layers table and pagination
        if (group.layers) {
          this.layersData = JSON.parse(JSON.stringify(group.layers));
          this.layerRowCount = this.layersData.length;
        }
      }, error => { }
    );

    // close modal
    this.modalService.dismissAll();
  }

}
