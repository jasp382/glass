import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

// Style
import { faPlus, faSearch, faTimes } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces
import { TableHeader } from 'src/app/interfaces/backoffice';
import { FirelocLayer } from 'src/app/interfaces/layers';
import { Group } from 'src/app/interfaces/users';


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

  constructor(
    private modalService: NgbModal
  ) { }

  ngOnInit(): void {
    
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

}
