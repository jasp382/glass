import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

// Style
import { faChevronDown, faPlus, faTimes, faTrash, faUserEdit, faUserFriends } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces
import { TableHeader } from 'src/app/interfaces/backoffice';
import { Group, UserAttr, UserAttrValue, UserProfile } from 'src/app/interfaces/users';

/**
 * Backoffice Users component.
 * 
 * Displays a list of FireLoc users. A single user can be created, viewed, edited or deleted.
 * It is also possible to filter the users with search terms or by user group.
 */
@Component({
  selector: 'boff-users',
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css']
})
export class UsersComponent implements OnInit {

  // icons
  /**
   * icon for group filter
   */
  groupIcon = faUserFriends;
  /**
   * icon for dropdown menus
   */
  dropIcon = faChevronDown;
  /**
   * icon for user creation
   */
  plusIcon = faPlus;
  /**
   * icon for user edition
   */
  userEditIcon = faUserEdit;
  /**
   * icon for user deletion
   */
  userDeleteIcon = faTrash;
  /**
   * icon to close information
   */
  closeIcon = faTimes;

  /**
   * list of users
   */
  users: UserProfile[] = [];
  /**
   * list of user attributes available
   */
  userAttributes: UserAttr[] = [];

  /**
   * list of user groups available
   */
  groups: Group[] = [];

  /**
   * list of table headers for table component
   */
  headers: TableHeader[] = [
    { objProperty: 'id', columnLabel: '#' },
    { objProperty: 'groupName', columnLabel: 'Grupo' },
    { objProperty: 'email', columnLabel: 'Email' },
    { objProperty: 'firstName', columnLabel: 'Primeiro Nome' },
    { objProperty: 'lastName', columnLabel: 'Apelidos' }
  ];

  // pagination
  /**
   * current page of data being displayed
   */
  currentPage: number = 1;
  /**
   * number of rows of data in the table
   */
  rowCount: number = this.users.length;

  // users search
  /**
   * list of selected user groups for data filtering
   */
  selectedGroups: string[] = [];
  /**
   * search terms for data filtering
   */
  searchTerms: string = '';

  // user details
  /**
   * list of headers to be displayed when a single user is closed
   */
  displayedHeaders: TableHeader[] = this.headers;
  /**
   * list of headers to be displayed when a single user is open
   */
  openHeaders: TableHeader[] = this.headers.filter((_, index) => index < 3);
  /**
   * flag to determine if a single user's information is being displayed 
   */
  isUserOpen: boolean = false;
  /**
   * reference to open user
   */
  openUser!: UserProfile;

  // create new user
  /**
   * new user form
   */
  newUserForm!: FormGroup;
  /**
   * new user data
   */
  newUser: UserProfile = { email: '', password: '', firstName: '', lastName: '', groupName: '' };

  // edit user
  /**
   * edit user form
   */
  editUserForm!: FormGroup;
  /**
   * reference to open user for editing
   */
  editUser: UserProfile = { ...this.openUser }

  // remove user
  /**
  * flag to determine if user has confirmed user removal
  */
  isConfChecked: boolean = false;
  /**
   * flag to determine if user has decided to remove a user
   */
  hasClickedRemove: boolean = false;

  constructor(
    private modalService: NgbModal
  ) { }

  /**
   * Initializes data and necessary forms (create and edit a user).
   */
  ngOnInit(): void {
    
  }

  /**
   * Updates search terms.
   * Searches users by email, first name, and last name in table component. 
   * See {@link TableComponent#filterDataSearchUsers} for more information.
   * @param searchTerms new search terms
   */
  searchUsers(searchTerms: string) {
    // ignore clear search event
    if (typeof (searchTerms) === 'string') this.searchTerms = searchTerms;
  }

}
