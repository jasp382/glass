import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { of, throwError } from 'rxjs';
import { FeatModule } from 'src/app/feat/feat.module';
import { Group, UserAttr, UserProfile } from 'src/app/interfaces/users';

import { UsersComponent } from './users.component';

describe('TS22 Backoffice UsersComponent', () => {
  let component: UsersComponent;
  let fixture: ComponentFixture<UsersComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [UsersComponent],
      imports: [
        HttpClientTestingModule,
        FeatModule,
        FontAwesomeModule,
      ]
    }).compileComponents();

    // component for testing
    fixture = TestBed.createComponent(UsersComponent);
    component = fixture.componentInstance;

    // trigger initial data binding
    fixture.detectChanges();
  });

  it('T22.1 should create', () => { expect(component).toBeTruthy(); });

  it('T22.2 should get users from API (group filter)', () => {
    // setup
    let getUsersSpy = spyOn(component, 'getUsers').and.callThrough();
    let usersAPISpy = spyOn(component['userServ'], 'getUsers').and.returnValue(of({ data: [{}] }));
    let userInfoSpy = spyOn(component, 'getUserInfo');
    let updateRowSpy = spyOn(component, 'updateRowCount');

    component.getUsers(true);

    // expectations
    expect(getUsersSpy).toHaveBeenCalledOnceWith(true);
    expect(usersAPISpy).toHaveBeenCalledOnceWith([]);
    expect(userInfoSpy).toHaveBeenCalledOnceWith([{}]);
    expect(updateRowSpy).toHaveBeenCalledOnceWith(0);
  });

  it('T22.3 should handle error of getting users from API (group filter)', () => {
    // setup
    let getUsersSpy = spyOn(component, 'getUsers').and.callThrough();
    let usersAPISpy = spyOn(component['userServ'], 'getUsers').and.returnValue(throwError(() => new Error()));
    let userInfoSpy = spyOn(component, 'getUserInfo');
    let updateRowSpy = spyOn(component, 'updateRowCount');

    component.getUsers(true);

    // expectations
    expect(getUsersSpy).toHaveBeenCalledOnceWith(true);
    expect(usersAPISpy).toHaveBeenCalledOnceWith([]);
    expect(userInfoSpy).not.toHaveBeenCalledOnceWith([{}]);
    expect(updateRowSpy).not.toHaveBeenCalledOnceWith(0);
  });

  it('T22.4 should get users from API (no group filter)', () => {
    // setup
    let getUsersSpy = spyOn(component, 'getUsers').and.callThrough();
    let usersAPISpy = spyOn(component['userServ'], 'getUsers').and.returnValue(of({ data: [{}] }));
    let userInfoSpy = spyOn(component, 'getUserInfo');
    let updateRowSpy = spyOn(component, 'updateRowCount');

    component.getUsers(false);

    // expectations
    expect(getUsersSpy).toHaveBeenCalledOnceWith(false);
    expect(usersAPISpy).toHaveBeenCalledOnceWith();
    expect(userInfoSpy).toHaveBeenCalledOnceWith([{}]);
    expect(updateRowSpy).toHaveBeenCalledOnceWith(0);
  });

  it('T22.5 should handle error of getting users from API (no group filter)', () => {
    // setup
    let getUsersSpy = spyOn(component, 'getUsers').and.callThrough();
    let usersAPISpy = spyOn(component['userServ'], 'getUsers').and.returnValue(throwError(() => new Error()));
    let userInfoSpy = spyOn(component, 'getUserInfo');
    let updateRowSpy = spyOn(component, 'updateRowCount');

    component.getUsers(false);

    // expectations
    expect(getUsersSpy).toHaveBeenCalledOnceWith(false);
    expect(usersAPISpy).toHaveBeenCalledOnceWith();
    expect(userInfoSpy).not.toHaveBeenCalledOnceWith([{}]);
    expect(updateRowSpy).not.toHaveBeenCalledOnceWith(0);
  });

  it('T22.6 should get user information from API response', () => {
    // setup
    let getInfoSpy = spyOn(component, 'getUserInfo').and.callThrough();
    let APIdata: any[] = [{
      attr: [{ attr: 1, value: 'value', attrname: 'name' }],
      active: false,
      email: 'email',
      first_name: 'name',
      last_name: 'surname',
      id: 1,
      usgroup: { name: 'fireloc' }
    },
    {
      attr: [],
      active: false,
      email: 'email',
      first_name: 'name',
      last_name: 'surname',
      id: 1,
      usgroup: null
    }];

    component.getUserInfo(APIdata);

    // expectations
    expect(getInfoSpy).toHaveBeenCalledOnceWith(APIdata);
    expect(component.users.length).toBe(2);
  });

  it('T22.7 should get groups from API', () => {
    // setup
    let getGroupsSpy = spyOn(component, 'getGroups').and.callThrough();
    let groupsAPISpy = spyOn(component['groupServ'], 'getGroups').and.returnValue(of({ data: [{ id: 1, name: 'name' }] }));

    component.getGroups();

    // expectations
    expect(getGroupsSpy).toHaveBeenCalledOnceWith();
    expect(groupsAPISpy).toHaveBeenCalledOnceWith(false, false);
    expect(component.groups.length).toBe(1);
  });

  it('T22.8 should handle error of getting groups from API', () => {
    // setup
    let getGroupsSpy = spyOn(component, 'getGroups').and.callThrough();
    let groupsAPISpy = spyOn(component['groupServ'], 'getGroups').and.returnValue(throwError(() => new Error()));

    component.getGroups();

    // expectations
    expect(getGroupsSpy).toHaveBeenCalledOnceWith();
    expect(groupsAPISpy).toHaveBeenCalledOnceWith(false, false);
    expect(component.groups.length).toBe(0);
  });

  it('T22.9 should get user attributes from API', () => {
    // setup
    let getAttributesSpy = spyOn(component, 'getUserAttributes').and.callThrough();
    let attrAPISpy = spyOn(component['userServ'], 'getUserAttributes').and.returnValue(of({
      data: [{ id: 1, slug: 'slug', name: 'name', type: 'str' }]
    }));

    component.getUserAttributes();

    // expectations
    expect(getAttributesSpy).toHaveBeenCalledOnceWith();
    expect(attrAPISpy).toHaveBeenCalledOnceWith();
    expect(component.userAttributes.length).toBe(1);
  });

  it('T22.10 should handle error of getting user attributes from API', () => {
    // setup
    let getAttributesSpy = spyOn(component, 'getUserAttributes').and.callThrough();
    let attrAPISpy = spyOn(component['userServ'], 'getUserAttributes').and.returnValue(throwError(() => new Error()));

    component.getUserAttributes();

    // expectations
    expect(getAttributesSpy).toHaveBeenCalledOnceWith();
    expect(attrAPISpy).toHaveBeenCalledOnceWith();
    expect(component.userAttributes.length).toBe(0);
  });

  it('T22.11 should get current page for table component', () => {
    // setup
    let pageSpy = spyOn(component, 'getPage').and.callThrough();

    component.getPage(5);

    // expectations
    expect(pageSpy).toHaveBeenCalledOnceWith(5);
    expect(component.currentPage).toBe(5);
  });

  it('T22.12 should update data row count for pagination', () => {
    // setup
    let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();

    component.updateRowCount(10);

    // expectations
    expect(rowSpy).toHaveBeenCalledOnceWith(10);
    expect(component.rowCount).toBe(10);
  });

  it('T22.13 should filter users by group', () => {
    // fake data
    let groups: Group[] = [{ id: 1, name: 'name1', selected: false }, { id: 2, name: 'name2', selected: false }];
    component.groups = groups;
    fixture.detectChanges();

    // spies
    let groupsSpy = spyOn(component, 'selectGroup').and.callThrough();
    let usersSpy = spyOn(component, 'getUsers');

    component.selectGroup(1);

    // expectations
    expect(groupsSpy).toHaveBeenCalledOnceWith(1);
    expect(usersSpy).toHaveBeenCalledOnceWith(true);
    expect(component.groups[0].selected).toBeTrue();
    expect(component.selectedGroups).toEqual(['name1']);
  });

  it('T22.14 should update search terms', () => {
    // spies
    let searchSpy = spyOn(component, 'searchUsers').and.callThrough();

    component.searchUsers(null as unknown as string);
    component.searchUsers('search');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('search');
    expect(component.searchTerms).toEqual('search');
  });

  it('T22.15 should open user details view', () => {
    // fake data
    let users: UserProfile[] = [
      { id: 1, email: 'email1', firstName: 'name1', lastName: 'surname1' },
      { id: 2, email: 'email2', firstName: 'name2', lastName: 'surname2' },
    ];
    component.users = users;
    fixture.detectChanges();

    // spies
    let userViewSpy = spyOn(component, 'toggleUserView').and.callThrough();

    component.toggleUserView(1);

    // expectations
    expect(userViewSpy).toHaveBeenCalledWith(1);
    expect(component.isUserOpen).toBeTrue();
    expect(component.displayedHeaders).toEqual(component.openHeaders);
    expect(component.openUser).toEqual({ id: 1, email: 'email1', firstName: 'name1', lastName: 'surname1' });
  });

  it('T22.16 should close user details view', () => {
    // fake data
    let users: UserProfile[] = [
      { id: 1, email: 'email1', firstName: 'name1', lastName: 'surname1' },
      { id: 2, email: 'email2', firstName: 'name2', lastName: 'surname2' },
    ];
    component.users = users;
    fixture.detectChanges();

    // spies
    let userViewSpy = spyOn(component, 'toggleUserView').and.callThrough();

    component.toggleUserView(-1);

    // expectations
    expect(userViewSpy).toHaveBeenCalledWith(-1);
    expect(component.isUserOpen).toBeFalse();
    expect(component.displayedHeaders).toEqual(component.headers);
  });

  describe('TS22.1 should open modal according to type', () => {
    it('T22.1.1 type: new', () => {
      // spies
      let openSpy = spyOn(component, 'open').and.callThrough();
      let initSpy = spyOn(component, 'initNewUser');
      let modalSpy = spyOn(component['modalService'], 'open');

      component.open({}, 'new');

      // expectations
      expect(openSpy).toHaveBeenCalledWith({}, 'new');
      expect(initSpy).toHaveBeenCalledWith();
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T22.1.2 type: edit', () => {
      // spies
      let openSpy = spyOn(component, 'open').and.callThrough();
      let initSpy = spyOn(component, 'initEditUser');
      let modalSpy = spyOn(component['modalService'], 'open');

      component.open({}, 'edit');

      // expectations
      expect(openSpy).toHaveBeenCalledWith({}, 'edit');
      expect(initSpy).toHaveBeenCalledWith();
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T22.1.3 type: delete', () => {
      // spies
      let openSpy = spyOn(component, 'open').and.callThrough();
      let modalSpy = spyOn(component['modalService'], 'open');

      component.open({}, 'delete');

      // expectations
      expect(openSpy).toHaveBeenCalledWith({}, 'delete');
      expect(component.isConfChecked).toBeFalse();
      expect(component.hasClickedRemove).toBeFalse();
      expect(modalSpy).toHaveBeenCalled();
    });
  });

  it('T22.17 should initialize values for new user form', () => {
    // fake data
    let userAttr: UserAttr[] = [
      { id: 1, slug: 'slug1', name: 'name1', type: 'str' },
      { id: 2, slug: 'slug2', name: 'name2', type: 'int' },
      { id: 3, slug: 'slug3', name: 'name3', type: 'float' },
      { id: 4, slug: 'slug4', name: 'name4', type: 'bool' },
    ];
    let groups: Group[] = [{ id: 1, name: 'name' }];
    component.userAttributes = userAttr;
    component.groups = groups;
    fixture.detectChanges();

    // spies
    let initSpy = spyOn(component, 'initNewUser').and.callThrough();

    component.initNewUser();

    // expectations
    expect(initSpy).toHaveBeenCalledWith();
    expect(component.newUser).toEqual({
      email: '',
      password: '',
      firstName: '',
      lastName: '',
      groupName: 'name'
    });
  });

  it('T22.18 should initialize data for edit user form (user with all optional attributes)', () => {
    // fake data
    let userAttr: UserAttr[] = [
      { id: 1, slug: 'slug1', name: 'name1', type: 'str' },
      { id: 2, slug: 'slug2', name: 'name2', type: 'int' },
      { id: 3, slug: 'slug3', name: 'name3', type: 'float' },
      { id: 4, slug: 'slug4', name: 'name4', type: 'bool' },
    ];
    let openUser: UserProfile = {
      email: 'email',
      firstName: 'name',
      lastName: 'surname',
      groupName: 'fireloc',
      attr: [
        { attrID: 1, value: 'value1', name: 'name1' },
        { attrID: 2, value: 'value2', name: 'name2' },
        { attrID: 3, value: 'value3', name: 'name3' },
        { attrID: 4, value: 'value4', name: 'name4' },
      ]
    };
    component.userAttributes = userAttr;
    component.openUser = openUser;
    fixture.detectChanges();

    // spies
    let initSpy = spyOn(component, 'initEditUser').and.callThrough();

    component.initEditUser();

    // expectations
    expect(initSpy).toHaveBeenCalledWith();
    expect(component.editUser).toEqual({
      email: openUser.email,
      firstName: 'name',
      lastName: 'surname',
      groupName: 'fireloc'
    });
  });

  it('T22.19 should initialize data for edit user form (user without optional attributes)', () => {
    // fake data
    let userAttr: UserAttr[] = [
      { id: 1, slug: 'slug1', name: 'name1', type: 'str' },
      { id: 2, slug: 'slug2', name: 'name2', type: 'int' },
      { id: 3, slug: 'slug3', name: 'name3', type: 'float' },
      { id: 4, slug: 'slug4', name: 'name4', type: 'bool' },
    ];
    let openUser: UserProfile = {
      email: 'email',
      firstName: 'name',
      lastName: 'surname',
      groupName: 'fireloc',
      attr: null
    };
    component.userAttributes = userAttr;
    component.openUser = openUser;
    fixture.detectChanges();

    // spies
    let initSpy = spyOn(component, 'initEditUser').and.callThrough();

    component.initEditUser();

    // expectations
    expect(initSpy).toHaveBeenCalledWith();
    expect(component.editUser).toEqual({
      email: openUser.email,
      firstName: 'name',
      lastName: 'surname',
      groupName: 'fireloc'
    });
  });

  it('T22.20 should update new user property when form changes', () => {
    // spies
    let updateSpy = spyOn(component, 'updateNewUserField').and.callThrough();

    component.updateNewUserField('name', 'firstName');

    // expectations
    expect(updateSpy).toHaveBeenCalledWith('name', 'firstName');
    expect(component.newUser.firstName).toEqual('name');
  });

  it('T22.21 should update edit user property when form changes', () => {
    // spies
    let updateSpy = spyOn(component, 'updateEditUserField').and.callThrough();

    component.updateEditUserField('name', 'firstName');

    // expectations
    expect(updateSpy).toHaveBeenCalledWith('name', 'firstName');
    expect(component.editUser.firstName).toEqual('name');
  });

  it('T22.22 should not create a new user if new user form is invalid', () => {
    // spies
    let createSpy = spyOn(component, 'createNewUser').and.callThrough();
    let addNormalAPISpy = spyOn(component['userServ'], 'addUser');
    let addSpecialAPISpy = spyOn(component['userServ'], 'addAdminUser');
    let getInfoSpy = spyOn(component, 'getUserInfo');
    let rowSpy = spyOn(component, 'updateRowCount');

    component.createNewUser();

    // expectations
    expect(createSpy).toHaveBeenCalled();
    expect(addNormalAPISpy).not.toHaveBeenCalled();
    expect(addSpecialAPISpy).not.toHaveBeenCalled();
    expect(getInfoSpy).not.toHaveBeenCalled();
    expect(rowSpy).not.toHaveBeenCalled();
  });

  it('T22.23 should create a new regular user', () => {
    // spies
    let createSpy = spyOn(component, 'createNewUser').and.callThrough();
    let addAPISpy = spyOn(component['userServ'], 'addUser').and.returnValue(of({
      data: [{ id: 1, slug: 'slug', name: 'name', type: 'str' }]
    }));
    let getInfoSpy = spyOn(component, 'getUserInfo');
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake user attributes list
    let userAttr: UserAttr[] = [
      { id: 1, slug: 'slug1', name: 'name1', type: 'str' },
      { id: 2, slug: 'slug2', name: 'name2', type: 'int' },
      { id: 3, slug: 'slug3', name: 'name3', type: 'float' },
      { id: 4, slug: 'slug4', name: 'name4', type: 'bool' },
    ];
    component.userAttributes = userAttr;

    // fake new user form controls
    component.newUserForm.addControl('slug1', new FormControl(null));
    component.newUserForm.addControl('slug2', new FormControl(null));
    component.newUserForm.addControl('slug3', new FormControl(null));
    component.newUserForm.addControl('slug4', new FormControl(null));

    // fake new user information
    component.newUser.email = 'email@email.com';
    component.newUser.password = 'password';
    component.newUser.firstName = 'name';
    component.newUser.lastName = 'surname';
    component.newUser.groupName = 'justauser';
    component.newUserForm.patchValue({
      groupName: 'justauser',
      firstName: 'name',
      lastName: 'surname',
      email: 'email@email.com',
      password: 'password',
      slug1: 'some value',
    });
    component.newUserForm.controls['slug1'].markAsDirty();
    fixture.detectChanges();

    component.createNewUser();

    // expectations
    const expectedUserData = {
      "email": 'email@email.com',
      "password": 'password',
      "first_name": 'name',
      "last_name": 'surname',
      "slug1": 'some value',
    }
    expect(createSpy).toHaveBeenCalledWith();
    expect(addAPISpy).toHaveBeenCalledWith(expectedUserData);
    expect(getInfoSpy).toHaveBeenCalled();
    expect(rowSpy).toHaveBeenCalled();
  });

  it('T22.24 should handle error on creating a new regular user', () => {
    // spies
    let createSpy = spyOn(component, 'createNewUser').and.callThrough();
    let addAPISpy = spyOn(component['userServ'], 'addUser').and.returnValue(throwError(() => new Error()));
    let getInfoSpy = spyOn(component, 'getUserInfo');
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake user attributes list
    let userAttr: UserAttr[] = [
      { id: 1, slug: 'slug1', name: 'name1', type: 'str' },
      { id: 2, slug: 'slug2', name: 'name2', type: 'int' },
      { id: 3, slug: 'slug3', name: 'name3', type: 'float' },
      { id: 4, slug: 'slug4', name: 'name4', type: 'bool' },
    ];
    component.userAttributes = userAttr;

    // fake new user form controls
    component.newUserForm.addControl('slug1', new FormControl(null));
    component.newUserForm.addControl('slug2', new FormControl(null));
    component.newUserForm.addControl('slug3', new FormControl(null));
    component.newUserForm.addControl('slug4', new FormControl(null));

    // fake new user information
    component.newUser.email = 'email@email.com';
    component.newUser.password = 'password';
    component.newUser.firstName = 'name';
    component.newUser.lastName = 'surname';
    component.newUser.groupName = 'justauser';
    component.newUserForm.patchValue({
      groupName: 'justauser',
      firstName: 'name',
      lastName: 'surname',
      email: 'email@email.com',
      password: 'password',
      slug1: 'some value',
    });
    component.newUserForm.controls['slug1'].markAsDirty();
    fixture.detectChanges();

    component.createNewUser();

    // expectations
    const expectedUserData = {
      "email": 'email@email.com',
      "password": 'password',
      "first_name": 'name',
      "last_name": 'surname',
      "slug1": 'some value',
    }
    expect(createSpy).toHaveBeenCalledWith();
    expect(addAPISpy).toHaveBeenCalledWith(expectedUserData);
    expect(getInfoSpy).not.toHaveBeenCalled();
    expect(rowSpy).not.toHaveBeenCalled();
  });

  it('T22.25 should create a new non-regular user', () => {
    // spies
    let createSpy = spyOn(component, 'createNewUser').and.callThrough();
    let addAPISpy = spyOn(component['userServ'], 'addAdminUser').and.returnValue(of({
      data: [{ id: 1, slug: 'slug', name: 'name', type: 'str' }]
    }));
    let getInfoSpy = spyOn(component, 'getUserInfo');
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake user attributes list
    let userAttr: UserAttr[] = [
      { id: 1, slug: 'slug1', name: 'name1', type: 'str' },
      { id: 2, slug: 'slug2', name: 'name2', type: 'int' },
      { id: 3, slug: 'slug3', name: 'name3', type: 'float' },
      { id: 4, slug: 'slug4', name: 'name4', type: 'bool' },
    ];
    component.userAttributes = userAttr;

    // fake new user form controls
    component.newUserForm.addControl('slug1', new FormControl(null));
    component.newUserForm.addControl('slug2', new FormControl(null));
    component.newUserForm.addControl('slug3', new FormControl(null));
    component.newUserForm.addControl('slug4', new FormControl(null));

    // fake new user information
    component.newUser.email = 'email@email.com';
    component.newUser.password = 'password';
    component.newUser.firstName = 'name';
    component.newUser.lastName = 'surname';
    component.newUser.groupName = 'fireloc';
    component.newUserForm.patchValue({
      groupName: 'fireloc',
      firstName: 'name',
      lastName: 'surname',
      email: 'email@email.com',
      password: 'password',
    });
    fixture.detectChanges();

    component.createNewUser();

    // expectations
    const expectedUserData = {
      "email": 'email@email.com',
      "password": 'password',
      "first_name": 'name',
      "last_name": 'surname',
      "group": 'fireloc',
    }
    expect(createSpy).toHaveBeenCalledWith();
    expect(addAPISpy).toHaveBeenCalledWith(expectedUserData);
    expect(getInfoSpy).toHaveBeenCalled();
    expect(rowSpy).toHaveBeenCalled();
  });

  it('T22.26 should handle error on creating a new non-regular user', () => {
    // spies
    let createSpy = spyOn(component, 'createNewUser').and.callThrough();
    let addAPISpy = spyOn(component['userServ'], 'addAdminUser').and.returnValue(throwError(() => new Error()));
    let getInfoSpy = spyOn(component, 'getUserInfo');
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake user attributes list
    let userAttr: UserAttr[] = [
      { id: 1, slug: 'slug1', name: 'name1', type: 'str' },
      { id: 2, slug: 'slug2', name: 'name2', type: 'int' },
      { id: 3, slug: 'slug3', name: 'name3', type: 'float' },
      { id: 4, slug: 'slug4', name: 'name4', type: 'bool' },
    ];
    component.userAttributes = userAttr;

    // fake new user form controls
    component.newUserForm.addControl('slug1', new FormControl(null));
    component.newUserForm.addControl('slug2', new FormControl(null));
    component.newUserForm.addControl('slug3', new FormControl(null));
    component.newUserForm.addControl('slug4', new FormControl(null));

    // fake new user information
    component.newUser.email = 'email@email.com';
    component.newUser.password = 'password';
    component.newUser.firstName = 'name';
    component.newUser.lastName = 'surname';
    component.newUser.groupName = 'fireloc';
    component.newUserForm.patchValue({
      groupName: 'fireloc',
      firstName: 'name',
      lastName: 'surname',
      email: 'email@email.com',
      password: 'password',
    });
    fixture.detectChanges();

    component.createNewUser();

    // expectations
    const expectedUserData = {
      "email": 'email@email.com',
      "password": 'password',
      "first_name": 'name',
      "last_name": 'surname',
      "group": 'fireloc',
    }
    expect(createSpy).toHaveBeenCalledWith();
    expect(addAPISpy).toHaveBeenCalledWith(expectedUserData);
    expect(getInfoSpy).not.toHaveBeenCalled();
    expect(rowSpy).not.toHaveBeenCalled();
  });

  it('T22.27 should not update user information if edit user form is invalid', () => {
    // spies
    let editSpy = spyOn(component, 'updateUser').and.callThrough();
    let editAPISpy = spyOn(component['userServ'], 'updateUser');

    component.updateUser();

    // expectations
    expect(editSpy).toHaveBeenCalledWith();
    expect(editAPISpy).not.toHaveBeenCalled();
  });

  it('T22.28 should update a user\'s information (not superuser)', () => {
    // spies
    let editSpy = spyOn(component, 'updateUser').and.callThrough();
    let editAPISpy = spyOn(component['userServ'], 'updateUser').and.returnValue(of({
      id: 1,
      email: 'email',
      active: false,
      first_name: 'name',
      last_name: 'surname',
      usgroup: 'justauser',
      attr: [{ attr: 1, value: 'some value', attrname: 'slug1' }]
    }));

    // fake user list
    let users: UserProfile[] = [{ id: 1, email: 'email@email.com', firstName: 'name', lastName: 'last' }];
    component.users = users;

    // fake user attributes list
    let userAttr: UserAttr[] = [
      { id: 1, slug: 'slug1', name: 'name1', type: 'str' },
      { id: 2, slug: 'slug2', name: 'name2', type: 'int' },
      { id: 3, slug: 'slug3', name: 'name3', type: 'float' },
      { id: 4, slug: 'slug4', name: 'name4', type: 'bool' },
    ];
    component.userAttributes = userAttr;

    // fake new user form controls
    component.editUserForm.addControl('slug1', new FormControl(null));
    component.editUserForm.addControl('slug2', new FormControl(null));
    component.editUserForm.addControl('slug3', new FormControl(null));
    component.editUserForm.addControl('slug4', new FormControl(null));

    // fake edit user information
    component.editUser.email = 'email@email.com';
    component.editUser.firstName = 'name';
    component.editUser.lastName = 'surname';
    component.editUser.groupName = 'justauser';
    component.editUserForm.patchValue({
      groupName: 'justauser',
      firstName: 'name',
      lastName: 'surname',
      email: 'email@email.com',
      slug1: 'some value',
    });
    component.editUserForm.controls['slug1'].markAsDirty();

    // fake open user data
    component.openUser = { email: 'email@email.com', firstName: 'name', lastName: 'last' };

    fixture.detectChanges();

    component.updateUser();

    // expectations
    const expectedUserData = {
      "email": 'email@email.com',
      "first_name": 'name',
      "last_name": 'surname',
      "group": "justauser",
      "slug1": 'some value',
    }
    expect(editSpy).toHaveBeenCalledWith();
    expect(editAPISpy).toHaveBeenCalledWith('email@email.com', expectedUserData);
  });

  it('T22.29 should update a user\'s information (superuser)', () => {
    // spies
    let editSpy = spyOn(component, 'updateUser').and.callThrough();
    let editAPISpy = spyOn(component['userServ'], 'updateUser').and.returnValue(of({
      id: 1,
      email: 'email',
      active: false,
      first_name: 'name',
      last_name: 'surname',
      usgroup: null,
      attr: []
    }));

    // fake user list
    let users: UserProfile[] = [{ id: 1, email: 'email@email.com', firstName: 'name', lastName: 'last' }];
    component.users = users;

    // fake user attributes list
    let userAttr: UserAttr[] = [
      { id: 1, slug: 'slug1', name: 'name1', type: 'str' },
      { id: 2, slug: 'slug2', name: 'name2', type: 'int' },
      { id: 3, slug: 'slug3', name: 'name3', type: 'float' },
      { id: 4, slug: 'slug4', name: 'name4', type: 'bool' },
    ];
    component.userAttributes = userAttr;

    // fake new user form controls
    component.editUserForm.addControl('slug1', new FormControl(null));
    component.editUserForm.addControl('slug2', new FormControl(null));
    component.editUserForm.addControl('slug3', new FormControl(null));
    component.editUserForm.addControl('slug4', new FormControl(null));

    // fake edit user information
    component.editUser.email = 'email@email.com';
    component.editUser.firstName = 'name';
    component.editUser.lastName = 'surname';
    component.editUser.groupName = 'superuser';
    component.editUserForm.patchValue({
      groupName: 'superuser',
      firstName: 'name',
      lastName: 'surname',
      email: 'email@email.com',
    });

    // fake open user data
    component.openUser = { email: 'email@email.com', firstName: 'name', lastName: 'last' };

    fixture.detectChanges();

    component.updateUser();

    // expectations
    const expectedUserData = {
      "email": 'email@email.com',
      "first_name": 'name',
      "last_name": 'surname',
      "group": "superuser",
    }
    expect(editSpy).toHaveBeenCalledWith();
    expect(editAPISpy).toHaveBeenCalledWith('email@email.com', expectedUserData);
  });

  it('T22.30 should handle error on updating a user\'s information', () => {
    // spies
    let editSpy = spyOn(component, 'updateUser').and.callThrough();
    let editAPISpy = spyOn(component['userServ'], 'updateUser').and.returnValue(throwError(() => new Error()));

    // fake user list
    let users: UserProfile[] = [{ id: 1, email: 'email@email.com', firstName: 'name', lastName: 'last' }];
    component.users = users;

    // fake user attributes list
    let userAttr: UserAttr[] = [
      { id: 1, slug: 'slug1', name: 'name1', type: 'str' },
      { id: 2, slug: 'slug2', name: 'name2', type: 'int' },
      { id: 3, slug: 'slug3', name: 'name3', type: 'float' },
      { id: 4, slug: 'slug4', name: 'name4', type: 'bool' },
    ];
    component.userAttributes = userAttr;

    // fake new user form controls
    component.editUserForm.addControl('slug1', new FormControl(null));
    component.editUserForm.addControl('slug2', new FormControl(null));
    component.editUserForm.addControl('slug3', new FormControl(null));
    component.editUserForm.addControl('slug4', new FormControl(null));

    // fake edit user information
    component.editUser.email = 'email@email.com';
    component.editUser.firstName = 'name';
    component.editUser.lastName = 'surname';
    component.editUser.groupName = 'justauser';
    component.editUserForm.patchValue({
      groupName: 'justauser',
      firstName: 'name',
      lastName: 'surname',
      email: 'email@email.com',
      slug1: 'some value',
    });
    component.editUserForm.controls['slug1'].markAsDirty();

    // fake open user data
    component.openUser = { email: 'email@email.com', firstName: 'name', lastName: 'last' };

    fixture.detectChanges();

    component.updateUser();

    // expectations
    const expectedUserData = {
      "email": 'email@email.com',
      "first_name": 'name',
      "last_name": 'surname',
      "group": "justauser",
      "slug1": 'some value',
    }
    expect(editSpy).toHaveBeenCalledWith();
    expect(editAPISpy).toHaveBeenCalledWith('email@email.com', expectedUserData);
  });

  it('T22.31 should not delete user information without confirmation', () => {
    // spies
    let deleteSpy = spyOn(component, 'removeUser').and.callThrough();
    let deleteAPISpy = spyOn(component['userServ'], 'deleteUser');

    component.removeUser();

    // expectations
    expect(deleteSpy).toHaveBeenCalledWith();
    expect(deleteAPISpy).not.toHaveBeenCalled();
  });

  it('T22.32 should delete user information if there was confirmation', () => {
    // spies
    let deleteSpy = spyOn(component, 'removeUser').and.callThrough();
    let deleteAPISpy = spyOn(component['userServ'], 'deleteUser').and.returnValue(of({}));
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake user list
    let users: UserProfile[] = [{ id: 1, email: 'email@email.com', firstName: 'name', lastName: 'last' }];
    component.users = users;
    // fake open user data
    component.openUser = { id: 1, email: 'email@email.com', firstName: 'name', lastName: 'last' };
    // fake confirmation
    component.isConfChecked = true;

    fixture.detectChanges();

    component.removeUser();

    // expectations
    expect(deleteSpy).toHaveBeenCalledWith();
    expect(deleteAPISpy).toHaveBeenCalledWith('email@email.com');
    expect(component.users).toEqual([]);
    expect(rowSpy).toHaveBeenCalledWith(0);
  });

  it('T22.33 should handle error on deleting user information if there was confirmation', () => {
    // spies
    let deleteSpy = spyOn(component, 'removeUser').and.callThrough();
    let deleteAPISpy = spyOn(component['userServ'], 'deleteUser').and.returnValue(throwError(() => new Error()));
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake user list
    let users: UserProfile[] = [{ id: 1, email: 'email@email.com', firstName: 'name', lastName: 'last' }];
    component.users = users;
    // fake open user data
    component.openUser = { id: 1, email: 'email@email.com', firstName: 'name', lastName: 'last' };
    // fake confirmation
    component.isConfChecked = true;

    fixture.detectChanges();

    component.removeUser();

    // expectations
    expect(deleteSpy).toHaveBeenCalledWith();
    expect(deleteAPISpy).toHaveBeenCalledWith('email@email.com');
    expect(component.users).toEqual(users);
    expect(rowSpy).not.toHaveBeenCalled();
  });

});
