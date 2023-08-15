import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { of, throwError } from 'rxjs';
import { FeatModule } from 'src/app/feat/feat.module';
import { FirelocLayer } from 'src/app/interfaces/layers';
import { Group } from 'src/app/interfaces/users';

import { GroupsComponent } from './groups.component';

describe('TS21 Backoffice GroupsComponent', () => {
  let component: GroupsComponent;
  let fixture: ComponentFixture<GroupsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [GroupsComponent],
      imports: [
        HttpClientTestingModule,
        FeatModule,
        FontAwesomeModule,
      ]
    }).compileComponents();

    // component for testing
    fixture = TestBed.createComponent(GroupsComponent);
    component = fixture.componentInstance;

    // trigger initial data binding
    fixture.detectChanges();
  });

  it('T21.1 should create', () => { expect(component).toBeTruthy(); });

  it('T21.2 should get groups from API', () => {
    // setup
    let expectedGroups = [{ id: 1, name: 'name', layers: [] }];
    let getGroupsSpy = spyOn(component, 'getGroups').and.callThrough();
    let groupsAPISpy = spyOn(component['groupServ'], 'getGroups').and.returnValue(of({
      data: expectedGroups,
    }));
    let updateRowSpy = spyOn(component, 'updateGroupRowCount');

    component.getGroups();

    // expectations
    expect(getGroupsSpy).toHaveBeenCalledOnceWith();
    expect(groupsAPISpy).toHaveBeenCalledOnceWith(false, true);
    expect(component.groups).toEqual(expectedGroups);
    expect(updateRowSpy).toHaveBeenCalledOnceWith(1);
  });

  it('T21.3 should handle error of getting groups from API ', () => {
    // setup
    let getGroupsSpy = spyOn(component, 'getGroups').and.callThrough();
    let groupsAPISpy = spyOn(component['groupServ'], 'getGroups').and.returnValue(throwError(() => new Error()));
    let updateRowSpy = spyOn(component, 'updateGroupRowCount');

    component.getGroups();

    // expectations
    expect(getGroupsSpy).toHaveBeenCalledOnceWith();
    expect(groupsAPISpy).toHaveBeenCalledOnceWith(false, true);
    expect(updateRowSpy).not.toHaveBeenCalled();
  });

  it('T21.4 should get layers from API', () => {
    // setup
    let expectedLayers = [{
      id: 1,
      designation: 'name',
      gsrvlyr: 'server',
      level: 1,
      rootid: 1,
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace'
    },
    {
      id: 1,
      designation: 'name',
      gsrvlyr: null,
      level: 1,
      rootid: 1,
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace'
    }];
    let getLayersSpy = spyOn(component, 'getLayers').and.callThrough();
    let layersAPISpy = spyOn(component['layerServ'], 'getLayersToken').and.returnValue(of({
      data: expectedLayers,
    }));
    let layerInfoSpy = spyOn(component, 'getLayerInfo').and.callThrough();

    component.getLayers();

    // expectations
    expect(getLayersSpy).toHaveBeenCalledOnceWith();
    expect(layersAPISpy).toHaveBeenCalledOnceWith(false);
    expect(layerInfoSpy).toHaveBeenCalledWith(expectedLayers);
    expect(component.layers.length).toBe(1);
  });

  it('T21.5 should handle error of getting layers from API ', () => {
    // setup
    let getLayersSpy = spyOn(component, 'getLayers').and.callThrough();
    let layersAPISpy = spyOn(component['layerServ'], 'getLayersToken').and.returnValue(throwError(() => new Error()));
    let layerInfoSpy = spyOn(component, 'getLayerInfo').and.callThrough();

    component.getLayers();

    // expectations
    expect(getLayersSpy).toHaveBeenCalledOnceWith();
    expect(layersAPISpy).toHaveBeenCalledOnceWith(false);
    expect(layerInfoSpy).not.toHaveBeenCalled();
    expect(component.layers.length).toBe(0);
  });

  it('T21.6 should update search terms', () => {
    // spies
    let searchSpy = spyOn(component, 'searchGroups').and.callThrough();

    component.searchGroups(null as unknown as string);
    component.searchGroups('search');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('search');
    expect(component.searchTerms).toEqual('search');
  });

  it('T21.7 should get current group page for table component', () => {
    // setup
    let pageSpy = spyOn(component, 'getGroupPage').and.callThrough();

    component.getGroupPage(5);

    // expectations
    expect(pageSpy).toHaveBeenCalledOnceWith(5);
    expect(component.currentGroupPage).toBe(5);
  });

  it('T21.8 should get current layer page for table component', () => {
    // setup
    let pageSpy = spyOn(component, 'getLayerPage').and.callThrough();

    component.getLayerPage(5);

    // expectations
    expect(pageSpy).toHaveBeenCalledOnceWith(5);
    expect(component.currentLayerPage).toBe(5);
  });

  it('T21.9 should open layers table', () => {
    // fake data
    let groups: Group[] = [
      { id: 1, name: 'name', layers: [] },
      { id: 2, name: 'name' },
    ];
    component.groups = groups;
    fixture.detectChanges();

    // spies
    let toggleLayersSpy = spyOn(component, 'toggleGroupLayers').and.callThrough();

    component.toggleGroupLayers(1);
    // expectations
    expect(toggleLayersSpy).toHaveBeenCalledWith(1);
    expect(component.isGroupOpen).toBeTrue();
    expect(component.selectedGroupID).toEqual(1);
    expect(component.layersData).toEqual([]);
    expect(component.layerRowCount).toEqual(0);

    component.toggleGroupLayers(2);
    // expectations
    expect(toggleLayersSpy).toHaveBeenCalledWith(2);
    expect(component.isGroupOpen).toBeTrue();
    expect(component.selectedGroupID).toEqual(2);
    expect(component.layerRowCount).toEqual(0);
  });

  it('T21.10 should close layers table', () => {
    // fake data
    let groups: Group[] = [
      { id: 1, name: 'name', layers: [] },
      { id: 2, name: 'name' },
    ];
    component.groups = groups;
    fixture.detectChanges();

    // spies
    let toggleLayersSpy = spyOn(component, 'toggleGroupLayers').and.callThrough();

    component.toggleGroupLayers(-1);
    // expectations
    expect(toggleLayersSpy).toHaveBeenCalledWith(-1);
    expect(component.isGroupOpen).toBeFalse();
    expect(component.selectedGroupID).toEqual(-1);
  });

  it('T21.11 should remove layer from group', () => {
    // fake data
    let groups: Group[] = [
      {
        id: 1, name: 'groupName', layers: [{
          id: 1, designation: 'layerName', slug: 'slug', serverLayer: 'server',
          store: 'store', style: 'style', workspace: 'work'
        }]
      },
    ];
    component.groups = groups;
    component.selectedGroupID = 1;
    fixture.detectChanges();

    // spies
    let unlinkLayerSpy = spyOn(component, 'unlinkLayer').and.callThrough();
    let layersAPISpy = spyOn(component['layerServ'], 'setGroupLayers').and.returnValue(of({}));

    component.unlinkLayer(1);

    // expectations
    expect(unlinkLayerSpy).toHaveBeenCalledOnceWith(1);
    expect(layersAPISpy).toHaveBeenCalledOnceWith('groupName', ['slug'], 'delete');
    expect(component.layersData).toEqual([]);
    expect(component.layerRowCount).toEqual(0);
  });

  it('T21.12 should not remove layer from group if layers are undefined', () => {
    // fake data
    let groups: Group[] = [{ id: 1, name: 'groupName' },];
    component.groups = groups;
    component.selectedGroupID = 1;
    fixture.detectChanges();

    // spies
    let unlinkLayerSpy = spyOn(component, 'unlinkLayer').and.callThrough();
    let layersAPISpy = spyOn(component['layerServ'], 'setGroupLayers').and.returnValue(of({}));

    component.unlinkLayer(1);

    // expectations
    expect(unlinkLayerSpy).toHaveBeenCalledOnceWith(1);
    expect(layersAPISpy).not.toHaveBeenCalled();
  });

  it('T21.13 should handle error of removing layer from group ', () => {
    // fake data
    let groups: Group[] = [
      {
        id: 1, name: 'groupName', layers: [{
          id: 1, designation: 'layerName', slug: 'slug', serverLayer: 'server',
          store: 'store', style: 'style', workspace: 'work'
        }]
      },
    ];
    component.groups = groups;
    component.selectedGroupID = 1;
    fixture.detectChanges();

    // spies
    let unlinkLayerSpy = spyOn(component, 'unlinkLayer').and.callThrough();
    let layersAPISpy = spyOn(component['layerServ'], 'setGroupLayers').and.returnValue(throwError(() => new Error()));

    component.unlinkLayer(1);

    // expectations
    expect(unlinkLayerSpy).toHaveBeenCalledOnceWith(1);
    expect(layersAPISpy).toHaveBeenCalledOnceWith('groupName', ['slug'], 'delete');
  });

  it('T21.14 should open modal for creating a new group', () => {
    // spies
    let openSpy = spyOn(component, 'open').and.callThrough();
    let modalSpy = spyOn(component['modalService'], 'open');

    component.open({}, -1);

    // expectations
    expect(openSpy).toHaveBeenCalledWith({}, -1);
    expect(modalSpy).toHaveBeenCalled();
  });

  it('T21.15 should open modal for editing or deleting a group', () => {
    // fake data
    let groups: Group[] = [
      {
        id: 1, name: 'groupName', layers: [{
          id: 1, designation: 'layerName', slug: 'slug', serverLayer: 'server',
          store: 'store', style: 'style', workspace: 'work'
        }]
      },
    ];
    component.groups = groups;
    fixture.detectChanges();

    // spies
    let openSpy = spyOn(component, 'open').and.callThrough();
    let modalSpy = spyOn(component['modalService'], 'open');

    component.open({}, 1);

    // expectations
    expect(openSpy).toHaveBeenCalledWith({}, 1);
    expect(modalSpy).toHaveBeenCalled();
    expect(component.isConfChecked).toBeFalse();
    expect(component.hasClickedRemove).toBeFalse();
    expect(component.selectedGroupID).toBe(1);
  });

  it('T21.16 should open modal for associating layers to a group', () => {
    // fake data
    let groups: Group[] = [
      {
        id: 1, name: 'groupName', layers: [{
          id: 1, designation: 'layerName', slug: 'slug', serverLayer: 'server',
          store: 'store', style: 'style', workspace: 'work'
        }]
      },
      { id: 2, name: 'groupName' },
    ];
    let layers: FirelocLayer[] = [
      {
        id: 1, designation: 'layerName', slug: 'slug', serverLayer: 'server',
        store: 'store', style: 'style', workspace: 'work'
      },
      {
        id: 2, designation: 'layerName', slug: 'slug', serverLayer: 'server',
        store: 'store', style: 'style', workspace: 'work'
      }
    ];
    component.groups = groups;
    component.layers = layers;
    component.selectedGroupID = 1;
    fixture.detectChanges();

    // spies
    let openSpy = spyOn(component, 'openLayerModal').and.callThrough();
    let modalSpy = spyOn(component['modalService'], 'open');

    component.openLayerModal({});

    // expectations
    expect(openSpy).toHaveBeenCalledWith({});
    expect(modalSpy).toHaveBeenCalled();
    expect(component.missingLayers).toEqual([layers[1]]);
    expect(component.filteredMissingLayers).toEqual([layers[1]]);

    // coverage for missing layers filter
    component.selectedGroupID = 2;
    fixture.detectChanges();
    component.openLayerModal({});
  });

  it('T21.17 should update new group name from new form input', () => {
    let openSpy = spyOn(component, 'updateNewGroupName').and.callThrough();
    component.updateNewGroupName('newName');
    expect(openSpy).toHaveBeenCalled();
    expect(component.newGroup.name).toEqual('newName');
  });

  it('T21.18 should update group name from edit form input', () => {
    component.editGroup = { id: 1, name: 'oldName' };
    fixture.detectChanges();
    let openSpy = spyOn(component, 'updateEditGroupName').and.callThrough();
    component.updateEditGroupName('editName');
    expect(openSpy).toHaveBeenCalled();
    expect(component.editGroup.name).toEqual('editName');
  });

  it('T21.19 should not create a new group if new group form is invalid', () => {
    // spies
    let createSpy = spyOn(component, 'createNewGroup').and.callThrough();
    let createAPISpy = spyOn(component['groupServ'], 'addGroup');
    let rowSpy = spyOn(component, 'updateGroupRowCount');

    component.createNewGroup();

    // expectations
    expect(createSpy).toHaveBeenCalled();
    expect(createAPISpy).not.toHaveBeenCalled();
    expect(rowSpy).not.toHaveBeenCalled();
  });

  it('T21.20 should create a new group', () => {
    // spies
    let createSpy = spyOn(component, 'createNewGroup').and.callThrough();
    let createAPISpy = spyOn(component['groupServ'], 'addGroup').and.returnValue(of({
      data: [{ id: 1, name: 'name' }]
    }));
    let rowSpy = spyOn(component, 'updateGroupRowCount');

    // fake new group information
    component.newGroup.name = 'name';
    component.newGroupForm.patchValue({ name: 'name' });
    fixture.detectChanges();

    component.createNewGroup();

    // expectations
    expect(createSpy).toHaveBeenCalledWith();
    expect(createAPISpy).toHaveBeenCalledWith('name');
    expect(rowSpy).toHaveBeenCalled();
  });

  it('T21.21 should handle error from creating a new group', () => {
    // spies
    let createSpy = spyOn(component, 'createNewGroup').and.callThrough();
    let createAPISpy = spyOn(component['groupServ'], 'addGroup').and.returnValue(throwError(() => new Error()));
    let rowSpy = spyOn(component, 'updateGroupRowCount');

    // fake new group information
    component.newGroup.name = 'name';
    component.newGroupForm.patchValue({ name: 'name' });
    fixture.detectChanges();

    component.createNewGroup();

    // expectations
    expect(createSpy).toHaveBeenCalledWith();
    expect(createAPISpy).toHaveBeenCalledWith('name');
    expect(rowSpy).not.toHaveBeenCalled();
  });

  it('T21.22 should not edit a group if group form is invalid', () => {
    // spies
    let updateSpy = spyOn(component, 'updateGroup').and.callThrough();
    let updateAPISpy = spyOn(component['groupServ'], 'updateGroup');

    component.updateGroup();

    // expectations
    expect(updateSpy).toHaveBeenCalled();
    expect(updateAPISpy).not.toHaveBeenCalled();
  });

  it('T21.23 should edit a group', () => {
    // spies
    let updateSpy = spyOn(component, 'updateGroup').and.callThrough();
    let updateAPISpy = spyOn(component['groupServ'], 'updateGroup').and.returnValue(of({
      id: 1, name: 'newName'
    }));

    // fake edit group information
    component.groups = [{ id: 1, name: 'oldName' }];
    component.editGroup = { id: 1, name: 'newName' };
    component.editGroupForm.patchValue({ name: 'newName' });
    fixture.detectChanges();

    component.updateGroup();

    // expectations
    expect(updateSpy).toHaveBeenCalledWith();
    expect(updateAPISpy).toHaveBeenCalledWith('oldName', 'newName');
    expect(component.groups).toEqual([{ id: 1, name: 'newName' }]);
  });

  it('T21.24 should handle error from editing a group', () => {
    // spies
    let updateSpy = spyOn(component, 'updateGroup').and.callThrough();
    let updateAPISpy = spyOn(component['groupServ'], 'updateGroup').and.returnValue(throwError(() => new Error()));

    // fake edit group information
    component.editGroup = { name: 'newName', id: 1 };
    component.groups = [{ id: 1, name: 'oldName' }];
    component.editGroupForm.patchValue({ name: 'newName' });
    fixture.detectChanges();

    component.updateGroup();

    // expectations
    expect(updateSpy).toHaveBeenCalledWith();
    expect(updateAPISpy).toHaveBeenCalledWith('oldName', 'newName');
    expect(component.groups).toEqual([{ id: 1, name: 'oldName' }]);
  });

  it('T21.25 should not remove a group if confirmation is not checked', () => {
    // spies
    let removeSpy = spyOn(component, 'deleteGroup').and.callThrough();
    let deleteAPISpy = spyOn(component['groupServ'], 'deleteGroup');

    component.deleteGroup();

    // expectations
    expect(removeSpy).toHaveBeenCalled();
    expect(deleteAPISpy).not.toHaveBeenCalled();
  });

  it('T21.26 should remove a group if confirmation is checked', () => {
    // spies
    let removeSpy = spyOn(component, 'deleteGroup').and.callThrough();
    let deleteAPISpy = spyOn(component['groupServ'], 'deleteGroup').and.returnValue(of({}));
    let rowSpy = spyOn(component, 'updateGroupRowCount');

    // fake group information
    component.groups = [{ id: 1, name: 'name' }];
    component.editGroup = { id: 1, name: 'name' };
    component.isConfChecked = true;
    fixture.detectChanges();

    component.deleteGroup();

    // expectations
    expect(removeSpy).toHaveBeenCalled();
    expect(deleteAPISpy).toHaveBeenCalled();
    expect(component.groups).toEqual([]);
    expect(rowSpy).toHaveBeenCalled();
    expect(component.isGroupOpen).toBeFalse();
    expect(component.selectedGroupID).toEqual(-1);
    expect(component.isConfChecked).toBeFalse();
    expect(component.hasClickedRemove).toBeFalse();
  });

  it('T21.27 should handle error from removing a group', () => {
    // spies
    let removeSpy = spyOn(component, 'deleteGroup').and.callThrough();
    let deleteAPISpy = spyOn(component['groupServ'], 'deleteGroup').and.returnValue(throwError(() => new Error()));
    let rowSpy = spyOn(component, 'updateGroupRowCount');

    // fake group information
    component.groups = [{ id: 1, name: 'name' }];
    component.editGroup = { id: 1, name: 'name' };
    component.isConfChecked = true;
    fixture.detectChanges();

    component.deleteGroup();

    // expectations
    expect(removeSpy).toHaveBeenCalled();
    expect(deleteAPISpy).toHaveBeenCalled();
    expect(component.groups).toEqual([{ id: 1, name: 'name' }]);
    expect(rowSpy).not.toHaveBeenCalled();
  });

  it('T21.28 should search layers', () => {
    let searchSpy = spyOn(component, 'searchLayers').and.callThrough();

    // fake layers information
    component.missingLayers = [{
      id: 1,
      designation: 'name',
      serverLayer: 'server',
      level: 1,
      rootID: 1,
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace'
    },
    {
      id: 2,
      designation: 'name2',
      serverLayer: 'server2',
      level: 2,
      rootID: 2,
      slug: 'slug2',
      store: 'store2',
      style: 'style2',
      workspace: 'workspace2'
    }];
    fixture.detectChanges();

    component.searchLayers('');
    component.searchLayers('name2');

    // expectations
    expect(searchSpy).toHaveBeenCalled();
    expect(component.filteredMissingLayers).toEqual([{
      id: 2,
      designation: 'name2',
      serverLayer: 'server2',
      level: 2,
      rootID: 2,
      slug: 'slug2',
      store: 'store2',
      style: 'style2',
      workspace: 'workspace2'
    }]);
  });

  it('T21.29 should select layer from check list to associate to group', () => {
    let selectSpy = spyOn(component, 'selectLayer').and.callThrough();

    // fake layers information
    component.missingLayers = [{
      id: 1,
      designation: 'name',
      serverLayer: 'server',
      level: 1,
      rootID: 1,
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace',
      selected: false
    },
    {
      id: 2,
      designation: 'name2',
      serverLayer: 'server2',
      level: 2,
      rootID: 2,
      slug: 'slug2',
      store: 'store2',
      style: 'style2',
      workspace: 'workspace2',
      selected: false
    }];
    fixture.detectChanges();

    component.selectLayer({ id: 2 });

    // expectations
    expect(selectSpy).toHaveBeenCalled();
    expect(component.missingLayers).toEqual([{
      id: 1,
      designation: 'name',
      serverLayer: 'server',
      level: 1,
      rootID: 1,
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace',
      selected: false
    },
    {
      id: 2,
      designation: 'name2',
      serverLayer: 'server2',
      level: 2,
      rootID: 2,
      slug: 'slug2',
      store: 'store2',
      style: 'style2',
      workspace: 'workspace2',
      selected: true
    }]);
  });

  it('T21.30 should associate new layers to a group', () => {
    let associateSpy = spyOn(component, 'associateLayers').and.callThrough();
    let setLayersAPISpy = spyOn(component['layerServ'], 'setGroupLayers').and.returnValue(of({}));

    component.missingLayers = [{
      id: 2,
      designation: 'name2',
      serverLayer: 'server2',
      level: 2,
      rootID: 2,
      slug: 'slug2',
      store: 'store2',
      style: 'style2',
      workspace: 'workspace2',
      selected: true,
    },
    {
      id: 3,
      designation: 'name3',
      serverLayer: 'server3',
      level: 3,
      rootID: 3,
      slug: 'slug3',
      store: 'store3',
      style: 'style3',
      workspace: 'workspace3',
      selected: false,
    }];
    component.groups = [{
      id: 1, name: 'name', layers: [{
        id: 1,
        designation: 'name',
        serverLayer: 'server',
        level: 1,
        rootID: 1,
        slug: 'slug',
        store: 'store',
        style: 'style',
        workspace: 'workspace',
        selected: false
      },]
    }];
    component.selectedGroupID = 1;
    fixture.detectChanges();

    component.associateLayers();

    expect(associateSpy).toHaveBeenCalled();
    expect(setLayersAPISpy).toHaveBeenCalledWith('name', ['slug', 'slug2'], 'add');
    expect(component.layerRowCount).toBe(2);
  });

  it('T21.31 should handle error from associating new layers to a group', () => {
    let associateSpy = spyOn(component, 'associateLayers').and.callThrough();
    let setLayersAPISpy = spyOn(component['layerServ'], 'setGroupLayers').and.returnValue(throwError(() => new Error()));

    component.missingLayers = [{
      id: 2,
      designation: 'name2',
      serverLayer: 'server2',
      level: 2,
      rootID: 2,
      slug: 'slug2',
      store: 'store2',
      style: 'style2',
      workspace: 'workspace2',
      selected: true,
    }];
    component.groups = [{
      id: 1, name: 'name', layers: [{
        id: 1,
        designation: 'name',
        serverLayer: 'server',
        level: 1,
        rootID: 1,
        slug: 'slug',
        store: 'store',
        style: 'style',
        workspace: 'workspace',
        selected: false
      },]
    }];
    component.selectedGroupID = 1;
    fixture.detectChanges();

    component.associateLayers();

    expect(associateSpy).toHaveBeenCalled();
    expect(setLayersAPISpy).toHaveBeenCalledWith('name', ['slug', 'slug2'], 'add');
    expect(component.layerRowCount).not.toBe(2);
  });

  it('T21.32 should assert that group has layers property before associating layers', () => {
    // just for coverage purposes
    let associateSpy = spyOn(component, 'associateLayers').and.callThrough();
    let setLayersAPISpy = spyOn(component['layerServ'], 'setGroupLayers').and.returnValue(of({}));

    component.missingLayers = [{
      id: 2,
      designation: 'name2',
      serverLayer: 'server2',
      level: 2,
      rootID: 2,
      slug: 'slug2',
      store: 'store2',
      style: 'style2',
      workspace: 'workspace2',
      selected: true,
    },
    {
      id: 3,
      designation: 'name3',
      serverLayer: 'server3',
      level: 3,
      rootID: 3,
      slug: 'slug3',
      store: 'store3',
      style: 'style3',
      workspace: 'workspace3',
      selected: false,
    }];
    component.groups = [{ id: 1, name: 'name' }];
    component.selectedGroupID = 1;
    fixture.detectChanges();

    component.associateLayers();

    expect(associateSpy).toHaveBeenCalled();
    expect(setLayersAPISpy).toHaveBeenCalledWith('name', ['slug2'], 'add');
    expect(component.layerRowCount).toBe(0);
  });
});
