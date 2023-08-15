import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

// Style
import { faChevronDown, faPlus, faTimes, faTrash, faUserEdit, faUserFriends } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces
import { TableHeader } from 'src/app/interfaces/backoffice';
import { Group, UserAttr, UserAttrValue, UserProfile } from 'src/app/interfaces/users';

// Services
import { UserService } from 'src/app/serv/rest/users/user.service';
import { GroupService } from 'src/app/serv/rest/users/group.service';

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

  /**
   * Empty constructor for the Backoffice Users component.
   * @param modalService Bootstrap modal service
   * @param userServ user service. See {@link UserService}.
   * @param groupServ group service. See {@link GroupService}.
   */
  constructor(private modalService: NgbModal, private userServ: UserService, private groupServ: GroupService) { }

  /**
   * Initializes data and necessary forms (create and edit a user).
   */
  ngOnInit(): void {
    // get users from API
    this.getUsers(false);

    // get groups from API
    this.getGroups();

    // get all optional user attributes
    this.getUserAttributes();

    // form new user creation
    this.newUserForm = new FormGroup({
      groupName: new FormControl(this.newUser.groupName, [Validators.required]),
      firstName: new FormControl(this.newUser.firstName, [Validators.required, Validators.maxLength(50)]),
      lastName: new FormControl(this.newUser.lastName, [Validators.required, Validators.maxLength(50)]),
      email: new FormControl(this.newUser.email, [
        Validators.required,
        Validators.email,
        Validators.pattern('^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,4}$'), // require top-level domain (.com, .uk, ...)
        Validators.maxLength(254)
      ]),
      password: new FormControl(this.newUser.password, [Validators.required]),
    });

    this.editUserForm = new FormGroup({
      groupName: new FormControl(this.editUser.groupName, [Validators.required]),
      firstName: new FormControl(this.editUser.firstName, [Validators.required, Validators.maxLength(50)]),
      lastName: new FormControl(this.editUser.lastName, [Validators.required, Validators.maxLength(50)]),
      email: new FormControl(this.editUser.email, [
        Validators.required,
        Validators.email,
        Validators.pattern('^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,4}$'), // require top-level domain (.com, .uk, ...)
        Validators.maxLength(254)
      ]),
    });
  }

  /**
   * Gets users data from API. Can get users without filter or filter results by selected user groups.
   * 
   * Updates the data displayed in the component.
   * @param filterGroup flag to determine if API should filter results by user group
   */
  getUsers(filterGroup: boolean) {
    if (filterGroup) {
      this.userServ.getUsers(this.selectedGroups).subscribe(
        (result: any) => {
          // get users
          this.getUserInfo(result.data);

          // update values for table and pagination
          this.users = JSON.parse(JSON.stringify(this.users));
          this.updateRowCount(this.users.length);
        }, error => { }
      );
    }
    else {
      this.userServ.getUsers().subscribe(
        (result: any) => {
          // get users
          this.getUserInfo(result.data);

          // update values for table and pagination
          this.users = JSON.parse(JSON.stringify(this.users));
          this.updateRowCount(this.users.length);
        }, error => { }
      );
    }
  }

  /**
   * Gets user information from API request response.
   * @param usersList API response data
   */
  getUserInfo(usersList: any[]) {
    usersList.forEach((u: any) => {
      // get user attributes
      let userAttributes: UserAttrValue[] = [];
      if (u.attr.length !== 0) {
        u.attr.forEach((a: any) => {
          let newAttribute: UserAttrValue = {
            attrID: a.attr,
            value: a.value,
            name: a.attrname
          };
          userAttributes.push(newAttribute);
        });
      }

      // compile user information
      let newUser: UserProfile = {
        active: u.active,
        email: u.email,
        firstName: u.first_name,
        lastName: u.last_name,
        id: u.id,
        groupName: u.usgroup !== null ? u.usgroup.name : 'superuser',
        attr: userAttributes,
      };
      this.users.push(newUser);
    });
  }

  /**
   * Gets user groups data from API
   */
  getGroups() {
    this.groupServ.getGroups(false, false).subscribe(
      (result: any) => {
        // add groups
        result.data.forEach((g: any) => {
          // compile group information
          let newGroup: Group = {
            id: g.id,
            name: g.name,
            selected: false,
          };
          this.groups.push(newGroup);
        });
      }, error => { }
    );
  }

  /**
   * Gets user attributes data from API.
   */
  getUserAttributes() {
    this.userServ.getUserAttributes().subscribe(
      (result: any) => {
        // add attributes
        result.data.forEach((a: any) => {
          // compile attribute information
          let newAttribute: UserAttr = {
            id: a.id,
            slug: a.slug,
            name: a.name,
            type: a.atype
          };
          this.userAttributes.push(newAttribute);
        });
      }, error => { }
    );
  }

  /**
   * Updates the current page of displayed data
   * @param page current page
   */
  getPage(page: any) { this.currentPage = page; }

  /**
   * Updates row count of filtered data for pagination
   * @param rows number of rows
   */
  updateRowCount(rows: number) { this.rowCount = rows; }

  /**
   * Selects user group and filter users with selected user groups.
   * @param groupID selected group ID
   */
  selectGroup(groupID: number) {
    let index = this.groups.findIndex(g => { return g.id === groupID });
    this.groups[index].selected = !this.groups[index].selected;

    // get selected groups for filtering
    this.selectedGroups = this.groups
      .filter(group => group.selected)
      .map(group => group.name);

    // filter users with groups
    this.users = [];
    this.getUsers(true);
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

  /**
   * Opens or closes a single user's information display.
   * @param userID user ID to display or -1 to close
   */
  toggleUserView(userID: number) {
    // close user details
    if (userID === -1) {
      this.isUserOpen = false;
      this.displayedHeaders = this.headers;
    }
    // open user details
    else {
      this.isUserOpen = true;
      this.displayedHeaders = this.openHeaders;

      // find user with selected user ID
      let userIndex = this.users.findIndex(item => item.id === userID);
      this.openUser = this.users[userIndex];
    }
  }

  /**
   * Opens modals to create, update or delete a user. Initializes the necessary data before opening a modal.
   * @param content modal content to display
   * @param modalType type of modal to open. Can be 'new', 'edit' or 'delete'
   */
  open(content: any, modalType: string) {
    // initialize according to modal
    switch (modalType) {
      case 'new':
        // initialize values
        this.initNewUser();
        break;
      case 'edit':
        // initialize values
        this.initEditUser();
        break;
      case 'delete':
        // reset variables for new modal
        this.isConfChecked = false;
        this.hasClickedRemove = false;
        break;
    }

    // open modal
    this.modalService.open(content, { centered: true, size: 'lg' });
  }

  /**
   * Initializes new user data
   */
  initNewUser() {
    // initialize required values in variable
    this.newUser.email = '';
    this.newUser.password = '';
    this.newUser.firstName = '';
    this.newUser.lastName = '';
    this.newUser.groupName = this.groups[0].name;

    // initialize required values in form control
    this.newUserForm.controls['email'].setValue(this.newUser.email);
    this.newUserForm.controls['password'].setValue(this.newUser.password);
    this.newUserForm.controls['firstName'].setValue(this.newUser.firstName);
    this.newUserForm.controls['lastName'].setValue(this.newUser.lastName);
    this.newUserForm.controls['groupName'].setValue(this.newUser.groupName);

    // initialize optional values in form control
    this.userAttributes.forEach((att) => {
      switch (att.type) {
        case 'str':
          this.newUserForm.addControl(att.slug, new FormControl(null, [Validators.maxLength(100)]));
          break;
        case 'int':
          this.newUserForm.addControl(att.slug, new FormControl(null, [Validators.min(0), Validators.maxLength(150)]));
          break;
        case 'float':
          this.newUserForm.addControl(att.slug, new FormControl(null, [
            Validators.min(0), Validators.max(150),
            Validators.pattern(/^[0-9]+(\.[0-9]{1,2})?$/)
          ]));
          break;
        case 'bool':
          this.newUserForm.addControl(att.slug, new FormControl(null));
          break;
      }
    });
  }

  /**
   * Initializes values to update user
   */
  initEditUser() {
    // initialize required values in variable
    this.editUser.email = this.openUser.email;
    this.editUser.firstName = this.openUser.firstName;
    this.editUser.lastName = this.openUser.lastName;
    this.editUser.groupName = this.openUser.groupName;

    // initialize required values in form control
    this.editUserForm.controls['email'].setValue(this.editUser.email);
    this.editUserForm.controls['firstName'].setValue(this.editUser.firstName);
    this.editUserForm.controls['lastName'].setValue(this.editUser.lastName);
    this.editUserForm.controls['groupName'].setValue(this.editUser.groupName);

    // get present optional user attributes in user
    let userAttributesID: number[] = [];
    if (this.openUser.attr) userAttributesID = this.openUser.attr.map(a => a.attrID);

    // initialize optional values in form control
    this.userAttributes.forEach((att) => {

      // remove control if it already exists
      this.editUserForm.removeControl(att.slug);

      switch (att.type) {
        case 'str':
          // if user has attribute, initialize with information
          if (this.openUser.attr && userAttributesID.includes(att.id)) {
            let attIndex = this.openUser.attr.findIndex(a => a.attrID === att.id);
            this.editUserForm.addControl(
              att.slug,
              new FormControl(this.openUser.attr[attIndex].value, [Validators.maxLength(100)])
            );
          }
          // user does not have attribute, initialize as null
          else
            this.editUserForm.addControl(att.slug, new FormControl(null, [Validators.maxLength(100)]));
          break;
        case 'int':
          // if user has attribute, initialize with information
          if (this.openUser.attr && userAttributesID.includes(att.id)) {
            let attIndex = this.openUser.attr.findIndex(a => a.attrID === att.id);
            this.editUserForm.addControl(
              att.slug,
              new FormControl(this.openUser.attr[attIndex].value, [Validators.min(0), Validators.maxLength(150)])
            );
          }
          // user does not have attribute, initialize as null
          else
            this.editUserForm.addControl(att.slug, new FormControl(null, [Validators.min(0), Validators.maxLength(150)]));
          break;
        case 'float':
          // if user has attribute, initialize with information
          if (this.openUser.attr && userAttributesID.includes(att.id)) {
            let attIndex = this.openUser.attr.findIndex(a => a.attrID === att.id);
            this.editUserForm.addControl(att.slug,
              new FormControl(this.openUser.attr[attIndex].value, [
                Validators.min(0), Validators.max(150),
                Validators.pattern(/^[0-9]+(\.[0-9]{1,2})?$/)]
              ));
          }
          // user does not have attribute, initialize as null
          else {
            this.editUserForm.addControl(att.slug, new FormControl(null, [
              Validators.min(0), Validators.max(150),
              Validators.pattern(/^[0-9]+(\.[0-9]{1,2})?$/)
            ]));
          }
          break;
        case 'bool':
          // if user has attribute, initialize with information
          if (this.openUser.attr && userAttributesID.includes(att.id)) {
            let attIndex = this.openUser.attr.findIndex(a => a.attrID === att.id);
            this.editUserForm.addControl(att.slug, new FormControl(this.openUser.attr[attIndex].value));
          }
          // user does not have attribute, initialize as null
          else
            this.editUserForm.addControl(att.slug, new FormControl(null));
          break;
      }
    });
  }

  /**
   * Updates new user information from create input form
   * @param value updated value
   * @param field new user property to update
   */
  updateNewUserField<K extends keyof UserProfile>(value: UserProfile[K], field: K) { this.newUser[field] = value; }

  /**
   * Updates user information from edit input form
   * @param value updated value
   * @param field edit user property to update
   */
  updateEditUserField<K extends keyof UserProfile>(value: UserProfile[K], field: K) { this.editUser[field] = value; }

  /**
   * Creates a new user with the API if new user form is valid.
   */
  createNewUser() {
    // check if form is valid
    if (this.newUserForm.valid) {
      // get mandatory user attributes
      let newUserData: any = {
        "email": this.newUser.email,
        "password": this.newUser.password,
        "first_name": this.newUser.firstName,
        "last_name": this.newUser.lastName,
        "group": this.newUser.groupName,
      };

      // get optional user attributes
      this.userAttributes.forEach((att) => {
        let control = this.newUserForm.controls[att.slug];
        // add attributes to new user data
        if (control.dirty && control.value !== null)
          newUserData[att.slug] = control.value;
      });

      // add new user according to chosen group
      switch (newUserData.group) {
        case 'justauser':
          delete newUserData.group;
          this.userServ.addUser(newUserData).subscribe(
            (result: any) => {
              // update users table and pagination
              this.getUserInfo([result]);
              this.users = JSON.parse(JSON.stringify(this.users));
              this.updateRowCount(this.users.length);
            }, error => { }
          );
          break;
        default:
          this.userServ.addAdminUser(newUserData).subscribe(
            (result: any) => {
              // update users table and pagination
              this.getUserInfo([result]);
              this.users = JSON.parse(JSON.stringify(this.users));
              this.updateRowCount(this.users.length);
            }, error => { }
          );
          break;
      }
    }

    // close and reset
    this.newUserForm.reset();
    this.modalService.dismissAll();
  }

  /**
   * Updates a user if edit user form is valid.
   */
  updateUser() {
    // check if form is valid
    if (this.editUserForm.valid) {
      // get mandatory user attributes
      let editUserData: any = {
        "email": this.editUser.email,
        "first_name": this.editUser.firstName,
        "last_name": this.editUser.lastName,
        "group": this.editUser.groupName,
      };

      // get optional user attributes
      this.userAttributes.forEach((att) => {
        let control = this.editUserForm.controls[att.slug];
        // add attributes to user data
        if (control.dirty && control.value !== null && control.value.length !== 0)
          editUserData[att.slug] = control.value;
      });

      // update user with API
      this.userServ.updateUser(this.openUser.email, editUserData).subscribe(
        (result: any) => {
          // get user reference
          let userIndex = this.users.findIndex(u => u.id === result.id);
          let user = this.users[userIndex];

          // get user attributes
          let userAttributes: UserAttrValue[] = [];
          if (result.attr.length !== 0) {
            result.attr.forEach((a: any) => {
              let newAttribute: UserAttrValue = {
                attrID: a.attr,
                value: a.value,
                name: a.attrname
              };
              userAttributes.push(newAttribute);
            });
          }

          // update user information
          user.active = result.active;
          user.email = result.email;
          user.firstName = result.first_name;
          user.lastName = result.last_name;
          user.groupName = result.usgroup !== null ? result.usgroup.name : 'superuser';
          user.attr = userAttributes;

          // update table data
          this.users = JSON.parse(JSON.stringify(this.users));
        }, error => { }
      );
    }

    // close and reset
    this.editUserForm.reset();
    this.modalService.dismissAll();
  }

  /**
   * Checks if the user has confirmed the removal of a FireLoc user.
   * 
   * If there is confirmation, delete a user with the API and update the displayed data.
   */
  removeUser() {
    this.hasClickedRemove = true;
    // without checked confirmation, show error
    if (this.isConfChecked) {
      // remove user with API
      this.userServ.deleteUser(this.openUser.email).subscribe(
        (result: any) => {
          // close user display
          this.isUserOpen = false;
          this.displayedHeaders = this.headers;

          // remove user from list
          let userIndex = this.users.findIndex(item => item.id === this.openUser.id);
          this.users.splice(userIndex, 1);

          // update users table and pagination
          this.users = JSON.parse(JSON.stringify(this.users));
          this.updateRowCount(this.users.length);
        }, error => { }
      );
      // close
      this.modalService.dismissAll();
    }
  }
}
