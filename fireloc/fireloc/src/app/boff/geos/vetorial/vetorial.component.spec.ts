import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormArray, FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { of, throwError } from 'rxjs';
import { FeatModule } from 'src/app/feat/feat.module';
import { VectorCategory, VectorDataset } from 'src/app/interfaces/geospatial';

import { VetorialComponent } from './vetorial.component';

describe('TS15 Backoffice VetorialComponent', () => {
  let component: VetorialComponent;
  let fixture: ComponentFixture<VetorialComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [VetorialComponent],
      imports: [
        HttpClientTestingModule,
        FeatModule,
        FontAwesomeModule
      ],
      providers: [
        FormBuilder
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(VetorialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T15.1 should create', () => { expect(component).toBeTruthy(); });

  it('T15.2 it should get levels from add dataset form', () => {
    let getSpy = spyOnProperty(component, 'newLevels').and.callThrough();
    let result = component.newLevels;
    expect(getSpy).toHaveBeenCalled();
    expect(result).toEqual(<FormArray>component.newDataForm.get('levels'));
  });

  it('T15.3 it should get levels from edit dataset form', () => {
    let getSpy = spyOnProperty(component, 'editLevels').and.callThrough();
    let result = component.editLevels;
    expect(getSpy).toHaveBeenCalled();
    expect(result).toEqual(<FormArray>component.editDataForm.get('levels'));
  });

  it('T15.4 it should add level to add dataset form', () => {
    let getSpy = spyOnProperty(component, 'newLevels').and.callThrough();
    let addSpy = spyOn(component, 'addNewLevels').and.callThrough();
    let createSpy = spyOn(component, 'createLevelGroup').and.callThrough();
    let result = component.newLevels;
    component.addNewLevels();
    expect(getSpy).toHaveBeenCalled();
    expect(addSpy).toHaveBeenCalled();
    expect(result).toEqual(<FormArray>component.newDataForm.get('levels'));
    expect(createSpy).toHaveBeenCalled();
  });

  it('T15.5 it should add level to edit dataset form', () => {
    let getSpy = spyOnProperty(component, 'editLevels').and.callThrough();
    let addSpy = spyOn(component, 'addEditLevels').and.callThrough();
    let createSpy = spyOn(component, 'createLevelGroup').and.callThrough();
    let result = component.editLevels;
    component.addEditLevels();
    expect(getSpy).toHaveBeenCalled();
    expect(addSpy).toHaveBeenCalled();
    expect(result).toEqual(<FormArray>component.editDataForm.get('levels'));
    expect(createSpy).toHaveBeenCalled();
  });

  it('T15.6 it should create levels for form group', () => {
    let createSpy = spyOn(component, 'createLevelGroup').and.callThrough();
    let result = component.createLevelGroup();
    expect(createSpy).toHaveBeenCalled();
    expect(result).toBeDefined();
  });

  it('T15.7 it should remove level from add dataset form', () => {
    let getSpy = spyOnProperty(component, 'newLevels').and.callThrough();
    let removeSpy = spyOn(component, 'removeNewLevel').and.callThrough();
    let result = component.newLevels;
    component.removeNewLevel(0);
    expect(getSpy).toHaveBeenCalled();
    expect(removeSpy).toHaveBeenCalled();
    expect(result).toEqual(<FormArray>component.newDataForm.get('levels'));
  });

  it('T15.8 it should remove level from edit dataset form', () => {
    let getSpy = spyOnProperty(component, 'editLevels').and.callThrough();
    let removeSpy = spyOn(component, 'removeEditLevel').and.callThrough();
    let result = component.editLevels;
    component.removeEditLevel(0);
    expect(getSpy).toHaveBeenCalled();
    expect(removeSpy).toHaveBeenCalled();
    expect(result).toEqual(<FormArray>component.editDataForm.get('levels'));
  });

  it('T15.9 should get datasets from API', () => {
    // setup
    let getSpy = spyOn(component, 'getDatasets').and.callThrough();
    let getAPISpy = spyOn(component['vecServ'], 'getVectorDatasets')
      .and.returnValue(of({
        data: [{
          id: 1, slug: '', name: '', description: '', source: '', refyear: null, refprod: null, gtype: '', catid: 1, dsetlevel: []
        }, {
          id: 2, slug: '', name: '', description: '', source: '', refyear: null, refprod: null, gtype: '', catid: 1, dsetlevel: [
            { id: 1, slug: '', name: '', description: '', level: 1 }
          ]
        },
        ]
      }));
    let dataSpy = spyOn(component, 'getDatasetData').and.callThrough();
    let levelSpy = spyOn(component, 'getDatasetLevels').and.callThrough();
    let rowSpy = spyOn(component, 'updateRowCount');

    component.getDatasets();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).toHaveBeenCalled();
    expect(levelSpy).toHaveBeenCalled();
    expect(rowSpy).toHaveBeenCalled();
    expect(component.datasets.length).not.toBe(0);
  });

  it('T15.10 should handle error from getting datasets from API', () => {
    // setup
    let getSpy = spyOn(component, 'getDatasets').and.callThrough();
    let getAPISpy = spyOn(component['vecServ'], 'getVectorDatasets')
      .and.returnValue(throwError(() => new Error()));
    let dataSpy = spyOn(component, 'getDatasetData').and.callThrough();
    let levelSpy = spyOn(component, 'getDatasetLevels').and.callThrough();
    let rowSpy = spyOn(component, 'updateRowCount');

    component.getDatasets();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).not.toHaveBeenCalled();
    expect(levelSpy).not.toHaveBeenCalled();
    expect(rowSpy).not.toHaveBeenCalled();
    expect(component.datasets.length).toBe(0);
  });

  it('T15.11 should get dataset categories from API', () => {
    // setup
    let getSpy = spyOn(component, 'getCategories').and.callThrough();
    let getAPISpy = spyOn(component['vecServ'], 'getVectorCategories')
      .and.returnValue(of({ data: [{ id: 1, slug: '', name: '', description: '' }] }));
    let dataSpy = spyOn(component, 'getCategoryData').and.callThrough();

    component.getCategories();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).toHaveBeenCalled();
    expect(component.categories.length).not.toBe(0);
  });

  it('T15.12 should handle error from getting dataset categories from API', () => {
    // setup
    let getSpy = spyOn(component, 'getCategories').and.callThrough();
    let getAPISpy = spyOn(component['vecServ'], 'getVectorCategories')
      .and.returnValue(throwError(() => new Error()));
    let dataSpy = spyOn(component, 'getCategoryData').and.callThrough();

    component.getCategories();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).not.toHaveBeenCalled();
    expect(component.categories.length).toBe(0);
  });

  describe('TS15.1 filter datasets', ()=>{
    it('T15.1.1 should filter datasets by category (no geometry selected)', () => {
      // fake data
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      let datasets: VectorDataset[] = [{
        id: 1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '',
        geometryType: 'POINT', categoryID: 1, datasetLevels: []
      }];
      component.categories = categories;
      component.datasets = datasets;
      fixture.detectChanges();
  
      // spies
      let selectSpy = spyOn(component, 'selectCategory').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();
  
      component.selectCategory(1); // id:1 -> selected true
      component.selectCategory(1); // id:1 -> selected false
  
      // expectations
      expect(selectSpy).toHaveBeenCalledWith(1);
      expect(component.categories[0].selected).toBeFalse();
      expect(component.selectedCategoriesIDs).toEqual([]);
      expect(component.selectedGeometryTypes).toEqual([]);
      expect(rowSpy).toHaveBeenCalled();
    });
  
    it('T15.1.2 should filter datasets by category (previous geometry selected)', () => {
      // fake data
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      let datasets: VectorDataset[] = [{
        id: 1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '',
        geometryType: 'POINT', categoryID: 1, datasetLevels: []
      }];
      component.categories = categories;
      component.datasets = datasets;
      component.selectedGeometryTypes = ['POINT'];
      fixture.detectChanges();
  
      // spies
      let selectSpy = spyOn(component, 'selectCategory').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();
  
      component.selectCategory(1); // id:1 -> selected true
      component.selectCategory(1); // id:1 -> selected false
  
      // expectations
      expect(selectSpy).toHaveBeenCalledWith(1);
      expect(component.categories[0].selected).toBeFalse();
      expect(component.selectedCategoriesIDs).toEqual([]);
      expect(component.selectedGeometryTypes).toEqual([]);
      expect(rowSpy).toHaveBeenCalled();
    });
  
    it('T15.1.3 should filter datasets by geometry type (no categories selected)', () => {
      // fake data
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      let datasets: VectorDataset[] = [{
        id: 1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '',
        geometryType: 'POINT', categoryID: 1, datasetLevels: []
      }];
      component.categories = categories;
      component.datasets = datasets;
      fixture.detectChanges();
  
      // spies
      let selectSpy = spyOn(component, 'selectGeometryType').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();
  
      component.selectGeometryType('POINT'); // index:0 -> selected true
      component.selectGeometryType('POINT'); // index:0 -> selected false
  
      // expectations
      expect(selectSpy).toHaveBeenCalledWith('POINT');
      expect(component.geometryTypes[0].selected).toBeFalse();
      expect(component.selectedCategoriesIDs).toEqual([]);
      expect(component.selectedGeometryTypes).toEqual([]);
      expect(rowSpy).toHaveBeenCalled();
    });
  
    it('T15.1.4 should filter datasets by geometry type (previous categories selected)', () => {
      // fake data
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      let datasets: VectorDataset[] = [{
        id: 1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '',
        geometryType: 'POINT', categoryID: 1, datasetLevels: []
      }];
      component.categories = categories;
      component.datasets = datasets;
      component.selectedCategoriesIDs = [1];
      fixture.detectChanges();
  
      // spies
      let selectSpy = spyOn(component, 'selectGeometryType').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();
  
      component.selectGeometryType('POINT'); // index:0 -> selected true
      component.selectGeometryType('POINT'); // index:0 -> selected false
  
      // expectations
      expect(selectSpy).toHaveBeenCalledWith('POINT');
      expect(component.geometryTypes[0].selected).toBeFalse();
      expect(component.selectedCategoriesIDs).toEqual([]);
      expect(component.selectedGeometryTypes).toEqual([]);
      expect(rowSpy).toHaveBeenCalled();
    });
  });

  it('T15.13 should update search terms', () => {
    // spies
    let searchSpy = spyOn(component, 'searchDatasets').and.callThrough();

    component.searchDatasets(null as unknown as string);
    component.searchDatasets('search');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('search');
    expect(component.searchTerms).toEqual('search');
  });

  it('T15.14 should update data row count for pagination', () => {
    // setup
    let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();
    component.updateRowCount(10);
    // expectations
    expect(rowSpy).toHaveBeenCalledOnceWith(10);
    expect(component.rowCount).toBe(10);
  });

  it('T15.15 should get current page for table component', () => {
    // setup
    let pageSpy = spyOn(component, 'getPage').and.callThrough();
    component.getPage(5);
    // expectations
    expect(pageSpy).toHaveBeenCalledOnceWith(5);
    expect(component.currentPage).toBe(5);
  });

  it('T15.16 should open dataset details view', () => {
    // fake data
    let categories: VectorCategory[] = [
      { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
      { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
    ];
    let datasets: VectorDataset[] = [{
      id: 1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '',
      geometryType: 'POINT', categoryID: 1, datasetLevels: []
    }];
    component.categories = categories;
    component.datasets = datasets;
    fixture.detectChanges();

    // spies
    let datasetViewSpy = spyOn(component, 'toggleDatasetView').and.callThrough();

    component.toggleDatasetView(1);

    // expectations
    expect(datasetViewSpy).toHaveBeenCalledWith(1);
    expect(component.isDatasetOpen).toBeTrue();
    expect(component.displayedHeaders).toEqual(component.openHeaders);
    expect(component.openDataset).toEqual(datasets[0]);
    expect(component.openDataset.category).toEqual(categories[0]);
  });

  it('T15.17 should close dataset details view', () => {
    // fake data
    let categories: VectorCategory[] = [
      { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
      { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
    ];
    let datasets: VectorDataset[] = [{
      id: 1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '',
      geometryType: 'POINT', categoryID: 1, datasetLevels: []
    }];
    component.categories = categories;
    component.datasets = datasets;
    fixture.detectChanges();

    // spies
    let datasetViewSpy = spyOn(component, 'toggleDatasetView').and.callThrough();

    component.toggleDatasetView(-1);

    // expectations
    expect(datasetViewSpy).toHaveBeenCalledWith(-1);
    expect(component.isDatasetOpen).toBeFalse();
    expect(component.displayedHeaders).toEqual(component.headers);
  });

  describe('TS15.2 should open modal according to type', () => {
    it('T15.2.1 type: new', () => {
      // spies
      let openSpy = spyOn(component, 'open').and.callThrough();
      let initSpy = spyOn(component, 'initNewData');
      let modalSpy = spyOn(component['modalService'], 'open');

      component.open({}, 'new');

      // expectations
      expect(openSpy).toHaveBeenCalledWith({}, 'new');
      expect(initSpy).toHaveBeenCalledWith();
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T15.2.2 type: edit', () => {
      // spies
      let openSpy = spyOn(component, 'open').and.callThrough();
      let initSpy = spyOn(component, 'initEditData');
      let modalSpy = spyOn(component['modalService'], 'open');

      component.open({}, 'edit');

      // expectations
      expect(openSpy).toHaveBeenCalledWith({}, 'edit');
      expect(initSpy).toHaveBeenCalledWith();
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T15.2.3 type: delete', () => {
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

  it('T15.18 should initialize values for new dataset form', () => {
    // fake data
    let categories: VectorCategory[] = [
      { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
      { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
    ];
    component.categories = categories;
    fixture.detectChanges();

    // spies
    let initSpy = spyOn(component, 'initNewData').and.callThrough();

    component.initNewData();

    // expectations
    expect(initSpy).toHaveBeenCalledWith();
    expect(component.newData).toEqual({
      id: -1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '', categoryID: -1,
      datasetLevels: [], geometryType: 'POINT', category: categories[0],
    });
  });

  it('T15.19 should initialize data for edit dataset form', () => {
    // fake data
    let openDataset: VectorDataset = {
      id: 1, slug: '', name: '', description: '', source: '', refYear: null, refProd: null, geometryType: '',
      categoryID: 0, datasetLevels: [{ id: 1, slug: '', name: '', description: '', level: 1 }]
    };
    component.openDataset = openDataset;
    fixture.detectChanges();

    // spies
    let initSpy = spyOn(component, 'initEditData').and.callThrough();

    component.initEditData();

    // expectations
    expect(initSpy).toHaveBeenCalledWith();
    expect(component.editData).toEqual(openDataset);
  });

  it('T15.20 should update new dataset property when form changes', () => {
    // fake data
    let categories: VectorCategory[] = [
      { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
      { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
    ];
    let newData: VectorDataset = {
      id: -1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '', categoryID: -1,
      datasetLevels: [], geometryType: 'POINT', category: categories[0],
    };
    component.newData = newData;
    fixture.detectChanges();
    // spies
    let updateSpy = spyOn(component, 'updateNewDataField').and.callThrough();
    component.updateNewDataField('newName', 'name');
    // expectations
    expect(updateSpy).toHaveBeenCalledWith('newName', 'name');
    expect(component.newData.name).toEqual('newName');
  });

  it('T15.21 should update edit dataset property when form changes', () => {
    // spies
    let updateSpy = spyOn(component, 'updateEditDataField').and.callThrough();
    component.updateEditDataField('newName', 'name');
    // expectations
    expect(updateSpy).toHaveBeenCalledWith('newName', 'name');
    expect(component.editData.name).toEqual('newName');
  });

  describe('TS15.3 create a new dataset', () => {
    it('T15.3.1 should not create a new dataset if new data form is invalid', () => {
      // spies
      let createSpy = spyOn(component, 'createNewDataset').and.callThrough();
      let addDatasetAPISpy = spyOn(component['vecServ'], 'addVectorDataset');
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let getInfoSpy = spyOn(component, 'getDatasetData');
      let rowSpy = spyOn(component, 'updateRowCount');
  
      component.createNewDataset();
  
      // expectations
      expect(createSpy).toHaveBeenCalled();
      expect(addDatasetAPISpy).not.toHaveBeenCalled();
      expect(getInfoSpy).not.toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
      expect(rowSpy).not.toHaveBeenCalled();
    });
  
    it('T15.3.2 should create a new dataset (no optional data)', () => {
      // spies
      let createSpy = spyOn(component, 'createNewDataset').and.callThrough();
      let addDatasetAPISpy = spyOn(component['vecServ'], 'addVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null, source: 'source', idtype: 1
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let getInfoSpy = spyOn(component, 'getDatasetData')
      let rowSpy = spyOn(component, 'updateRowCount');
  
      // fake new dataset information
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.newData = {
        id: -1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: '',
        categoryID: -1, datasetLevels: [], geometryType: 'POINT', category: categories[0],
      };
      component.newDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      fixture.detectChanges();
  
      component.createNewDataset();
  
      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addDatasetAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
      expect(getInfoSpy).toHaveBeenCalled();
      expect(rowSpy).toHaveBeenCalled();
    });

    it('T15.3.3 should create a new dataset (optional data)', () => {
      // spies
      let createSpy = spyOn(component, 'createNewDataset').and.callThrough();
      let addDatasetAPISpy = spyOn(component['vecServ'], 'addVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null,
        source: 'source', gtype: 'POINT', catid: 1, dsetlevel: []
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', level: 1,
      }));
      let getInfoSpy = spyOn(component, 'getDatasetData').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new dataset information
      component.newData = {
        id: -1, slug: 'slug', name: 'name', description: 'desc', refYear: 1998, refProd: 2022, source: '',
        categoryID: -1, datasetLevels: [], geometryType: 'POINT',
      };
      component.newDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.newLevels.push(new FormGroup({
        levelID: new FormControl(null),
        levelSlug: new FormControl('slug'),
        levelLevel: new FormControl(1),
        levelName: new FormControl('name'),
        levelDescription: new FormControl('desc'),
      }));
      fixture.detectChanges();

      component.createNewDataset();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addDatasetAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).toHaveBeenCalled();
      expect(getInfoSpy).toHaveBeenCalled();
      expect(rowSpy).toHaveBeenCalled();
    });

    it('T15.3.4 should create a new dataset (optional data - check form controls)', () => {
      // spies
      let createSpy = spyOn(component, 'createNewDataset').and.callThrough();
      let addDatasetAPISpy = spyOn(component['vecServ'], 'addVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null,
        source: 'source', gtype: 'POINT', catid: 1, dsetlevel: []
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', level: 1,
      }));
      let getInfoSpy = spyOn(component, 'getDatasetData').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new dataset information
      component.newData = {
        id: -1, slug: 'slug', name: 'name', description: 'desc', refYear: 1998, refProd: 2022, source: '',
        categoryID: -1, datasetLevels: [], geometryType: 'POINT',
      };
      component.newDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.newLevels.push(new FormGroup({
        fake: new FormControl(null),
      }));
      fixture.detectChanges();

      component.createNewDataset();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addDatasetAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).toHaveBeenCalled();
      expect(getInfoSpy).toHaveBeenCalled();
      expect(rowSpy).toHaveBeenCalled();
    });

    it('T15.3.5 should handle error while adding levels from creating a new dataset', () => {
      // spies
      let createSpy = spyOn(component, 'createNewDataset').and.callThrough();
      let addDatasetAPISpy = spyOn(component['vecServ'], 'addVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null,
        source: 'source', gtype: 'POINT', catid: 1, dsetlevel: []
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel').and.returnValue(throwError(() => new Error()));
      let getInfoSpy = spyOn(component, 'getDatasetData').and.callThrough();
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new dataset information
      component.newData = {
        id: -1, slug: 'slug', name: 'name', description: 'desc', refYear: 1998, refProd: 2022, source: '',
        categoryID: -1, datasetLevels: [], geometryType: 'POINT',
      };
      component.newDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.newLevels.push(new FormGroup({
        levelID: new FormControl(null),
        levelSlug: new FormControl('slug'),
        levelLevel: new FormControl(1),
        levelName: new FormControl('name'),
        levelDescription: new FormControl('desc'),
      }));
      fixture.detectChanges();

      component.createNewDataset();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addDatasetAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).toHaveBeenCalled();
      expect(getInfoSpy).toHaveBeenCalled();
      expect(rowSpy).toHaveBeenCalled();
      expect(component.datasets[0].datasetLevels).toEqual([]);
    });

    it('T15.3.6 should handle error while adding a new dataset', () => {
      // spies
      let createSpy = spyOn(component, 'createNewDataset').and.callThrough();
      let addDatasetAPISpy = spyOn(component['vecServ'], 'addVectorDataset').and.returnValue(throwError(() => new Error()));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let getInfoSpy = spyOn(component, 'getDatasetData');
      let rowSpy = spyOn(component, 'updateRowCount');

      // fake new dataset information
      component.newData = {
        id: -1, slug: 'slug', name: 'name', description: 'desc', refYear: 1998, refProd: 2022, source: '',
        categoryID: -1, datasetLevels: [], geometryType: 'POINT',
      };
      component.newDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.newLevels.push(new FormGroup({
        levelID: new FormControl(null),
        levelSlug: new FormControl('slug'),
        levelLevel: new FormControl(1),
        levelName: new FormControl('name'),
        levelDescription: new FormControl('desc'),
      }));
      fixture.detectChanges();

      component.createNewDataset();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addDatasetAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
      expect(getInfoSpy).not.toHaveBeenCalled();
      expect(rowSpy).not.toHaveBeenCalled();
      expect(component.datasets.length).toEqual(0);
    });
  });

  describe('TS15.4 update an existing dataset', () => {
    it('T15.4.1 should not update a dataset if edit data form is invalid', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset');
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel');
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel');

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateDatasetAPISpy).not.toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
      expect(updateLevelAPISpy).not.toHaveBeenCalled();
      expect(removeLevelAPISpy).not.toHaveBeenCalled();
    });

    it('T15.4.2 should update a dataset (edit existing level)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null, source: 'source',
        catid: 1, gtype: 'POINT',
        dsetlevel: [{ id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }],
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', level: 1
      }));
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel');

      // fake datasets
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [
          { id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }
        ],
      }];
      // fake categories
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.datasets = datasets;
      component.categories = categories;
      component.openDataset = datasets[0];
      fixture.detectChanges();

      // fake edit dataset information
      component.editData = {
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: NaN, refProd: NaN, source: 'source',
        geometryType: 'POINT', categoryID: 1, category: categories[0], datasetLevels: [
          { id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }
        ],
      };
      component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.editLevels.push(new FormGroup({
        levelID: new FormControl(1),
        levelSlug: new FormControl('slug'),
        levelLevel: new FormControl(1),
        levelName: new FormControl('name'),
        levelDescription: new FormControl('desc'),
      }));
      fixture.detectChanges();

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateDatasetAPISpy).toHaveBeenCalled();
      expect(updateLevelAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
      expect(removeLevelAPISpy).not.toHaveBeenCalled();
    });

    it('T15.4.3 should handle error while editing an existing dataset level', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null, source: 'source',
        catid: 1, gtype: 'POINT',
        dsetlevel: [{ id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }],
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel').and.returnValue(throwError(() => new Error()));
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel');

      // fake datasets
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [
          { id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }
        ],
      }];
      // fake categories
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.datasets = datasets;
      component.categories = categories;
      component.openDataset = datasets[0];
      fixture.detectChanges();

      // fake edit dataset information
      component.editData = {
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: NaN, refProd: NaN, source: 'source',
        geometryType: 'POINT', categoryID: 1, category: categories[0], datasetLevels: [
          { id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }
        ],
      };
      component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.editLevels.push(new FormGroup({
        levelID: new FormControl(1),
        levelSlug: new FormControl('slug'),
        levelLevel: new FormControl(1),
        levelName: new FormControl('name'),
        levelDescription: new FormControl('desc'),
      }));
      fixture.detectChanges();

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateDatasetAPISpy).toHaveBeenCalled();
      expect(updateLevelAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
      expect(removeLevelAPISpy).not.toHaveBeenCalled();
    });

    it('T15.4.4 should check form controls while updating a dataset (edit existing level)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null, source: 'source',
        catid: 1, gtype: 'POINT',
        dsetlevel: [{ id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }],
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', level: 1
      }));
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel');

      // fake datasets
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [
          { id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }
        ],
      }];
      // fake categories
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.datasets = datasets;
      component.categories = categories;
      component.openDataset = datasets[0];
      fixture.detectChanges();

      // fake edit dataset information
      component.editData = {
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: 1998, refProd: 2022, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [
          { id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }
        ],
      };
      component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.editLevels.push(new FormGroup({
        levelID: new FormControl(1),
      }));
      fixture.detectChanges();

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateDatasetAPISpy).toHaveBeenCalled();
      expect(updateLevelAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
      expect(removeLevelAPISpy).not.toHaveBeenCalled();
    });

    it('T15.4.5 should update a dataset (add new level)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null, source: 'source',
        catid: 1, gtype: 'POINT', dsetlevel: [],
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', level: 1
      }));
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel');
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel');

      // fake datasets
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [],
      }];
      // fake categories
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.datasets = datasets;
      component.categories = categories;
      component.openDataset = datasets[0];
      fixture.detectChanges();

      // fake edit dataset information
      component.editData = {
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: NaN, refProd: NaN, source: 'source',
        geometryType: 'POINT', categoryID: 1, category: categories[0], datasetLevels: [],
      };
      component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.editLevels.push(new FormGroup({
        levelID: new FormControl(null),
        levelSlug: new FormControl('slug'),
        levelLevel: new FormControl(1),
        levelName: new FormControl('name'),
        levelDescription: new FormControl('desc'),
      }));
      fixture.detectChanges();

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateDatasetAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).toHaveBeenCalled();
      expect(updateLevelAPISpy).not.toHaveBeenCalled();
      expect(removeLevelAPISpy).not.toHaveBeenCalled();
    });

    it('T15.4.6 should handle error while updating a dataset (add new level)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null, source: 'source',
        catid: 1, gtype: 'POINT', dsetlevel: [],
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel').and.returnValue(throwError(() => new Error()));
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel');
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel');

      // fake datasets
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [],
      }];
      // fake categories
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.datasets = datasets;
      component.categories = categories;
      component.openDataset = datasets[0];
      fixture.detectChanges();

      // fake edit dataset information
      component.editData = {
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: NaN, refProd: NaN, source: 'source',
        geometryType: 'POINT', categoryID: 1, category: categories[0], datasetLevels: [],
      };
      component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.editLevels.push(new FormGroup({
        levelID: new FormControl(null),
        levelSlug: new FormControl('slug'),
        levelLevel: new FormControl(1),
        levelName: new FormControl('name'),
        levelDescription: new FormControl('desc'),
      }));
      fixture.detectChanges();

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateDatasetAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).toHaveBeenCalled();
      expect(updateLevelAPISpy).not.toHaveBeenCalled();
      expect(removeLevelAPISpy).not.toHaveBeenCalled();
    });

    it('T15.4.7 should check form controls while updating a dataset (add new level)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null, source: 'source',
        catid: 1, gtype: 'POINT', dsetlevel: [],
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', level: 1
      }));
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel');
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel');

      // fake datasets
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [],
      }];
      // fake categories
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.datasets = datasets;
      component.categories = categories;
      component.openDataset = datasets[0];
      fixture.detectChanges();

      // fake edit dataset information
      component.editData = {
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: NaN, refProd: NaN, source: 'source',
        geometryType: 'POINT', categoryID: 1, category: categories[0], datasetLevels: [],
      };
      component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.editLevels.push(new FormGroup({
        levelID: new FormControl(null),
      }));
      fixture.detectChanges();

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateDatasetAPISpy).toHaveBeenCalled();
      expect(addLevelAPISpy).toHaveBeenCalled();
      expect(updateLevelAPISpy).not.toHaveBeenCalled();
      expect(removeLevelAPISpy).not.toHaveBeenCalled();
    });

    it('T15.4.8 should update a dataset (delete existing level)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null, source: 'source',
        catid: 1, gtype: 'POINT',
        dsetlevel: [{ id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }],
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel');
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel').and.returnValue(of({}));

      // fake datasets
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [
          { id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }
        ],
      }];
      // fake categories
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.datasets = datasets;
      component.categories = categories;
      component.openDataset = datasets[0];
      fixture.detectChanges();

      // fake edit dataset information
      component.editData = {
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: NaN, refProd: NaN, source: 'source',
        geometryType: 'POINT', categoryID: 1, category: categories[0], datasetLevels: [
          { id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }
        ],
      };
      component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      fixture.detectChanges();

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateDatasetAPISpy).toHaveBeenCalled();
      expect(removeLevelAPISpy).toHaveBeenCalled();
      expect(updateLevelAPISpy).not.toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
    });

    it('T15.4.9 should handle error while updating a dataset (delete existing level)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null, source: 'source',
        catid: 1, gtype: 'POINT',
        dsetlevel: [{ id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }],
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel');
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel').and.returnValue(throwError(() => new Error()));

      // fake datasets
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [
          { id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }
        ],
      }];
      // fake categories
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.datasets = datasets;
      component.categories = categories;
      component.openDataset = datasets[0];
      fixture.detectChanges();

      // fake edit dataset information
      component.editData = {
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: NaN, refProd: NaN, source: 'source',
        geometryType: 'POINT', categoryID: 1, category: categories[0], datasetLevels: [
          { id: 1, slug: 'slug', name: 'name', description: 'description', level: 1 }
        ],
      };
      component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      fixture.detectChanges();

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateDatasetAPISpy).toHaveBeenCalled();
      expect(removeLevelAPISpy).toHaveBeenCalled();
      expect(updateLevelAPISpy).not.toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
    });

    it('T15.4.10 should check form controls while updating a dataset', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset').and.returnValue(of({
        id: 1, slug: 'slug', name: 'name', description: 'desc', refyear: null, refprod: null, source: 'source',
        catid: 1, gtype: 'POINT', dsetlevel: [],
      }));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel');
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel');

      // fake datasets
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [],
      }];
      // fake categories
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.datasets = datasets;
      component.categories = categories;
      component.openDataset = datasets[0];
      fixture.detectChanges();

      // fake edit dataset information
      component.editData = {
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: 1998, refProd: 2022, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [],
      };
      component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.editLevels.push(new FormGroup({ fake: new FormControl(1), }));
      fixture.detectChanges();

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateDatasetAPISpy).toHaveBeenCalled();
      expect(updateLevelAPISpy).not.toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
      expect(removeLevelAPISpy).not.toHaveBeenCalled();
    });

    it('T15.4.11 should handle error while updating a dataset', () => {
      // spies
      let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
      let updateDatasetAPISpy = spyOn(component['vecServ'], 'updateVectorDataset').and.returnValue(throwError(() => new Error()));
      let addLevelAPISpy = spyOn(component['vecServ'], 'addVectorLevel');
      let updateLevelAPISpy = spyOn(component['vecServ'], 'updateVectorLevel');
      let removeLevelAPISpy = spyOn(component['vecServ'], 'deleteVectorLevel');

      // fake datasets
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: null, refProd: null, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [],
      }];
      // fake categories
      let categories: VectorCategory[] = [
        { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
        { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
      ];
      component.datasets = datasets;
      component.categories = categories;
      component.openDataset = datasets[0];
      fixture.detectChanges();

      // fake edit dataset information
      component.editData = {
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: 1998, refProd: 2022, source: 'source',
        geometryType: 'POINT', categoryID: 1, datasetLevels: [],
      };
      component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
      component.editLevels.push(new FormGroup({ fake: new FormControl(1), }));
      fixture.detectChanges();

      component.updateDataset();

      // expectations
      expect(updateSpy).toHaveBeenCalledWith();
      expect(updateDatasetAPISpy).toHaveBeenCalled();
      expect(updateLevelAPISpy).not.toHaveBeenCalled();
      expect(addLevelAPISpy).not.toHaveBeenCalled();
      expect(removeLevelAPISpy).not.toHaveBeenCalled();
    });
  });

  describe('TS15.5 delete an existing dataset', () => {
    it('T15.5.1 should not delete dataset without confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeDataset').and.callThrough();
      let deleteAPISpy = spyOn(component['vecServ'], 'deleteVectorDataset');
  
      component.removeDataset();
  
      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).not.toHaveBeenCalled();
    });
  
    it('T15.5.2 should delete dataset if there was confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeDataset').and.callThrough();
      let deleteAPISpy = spyOn(component['vecServ'], 'deleteVectorDataset').and.returnValue(of({}));
      let rowSpy = spyOn(component, 'updateRowCount');
  
      // fake information
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: 1998, refProd: 2022, source: '',
        categoryID: 1, datasetLevels: [], geometryType: 'POINT',
      }];
      component.datasets = datasets;
      component.openDataset = datasets[0];
      component.isConfChecked = true;
      fixture.detectChanges();
  
      component.removeDataset();
  
      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).toHaveBeenCalledWith('slug');
      expect(component.datasets).toEqual([]);
      expect(component.isDatasetOpen).toBeFalse();
      expect(component.displayedHeaders).toEqual(component.headers);
      expect(rowSpy).toHaveBeenCalledWith(0);
    });
  
    it('T15.5.3 should handle error on deleting dataset if there was confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeDataset').and.callThrough();
      let deleteAPISpy = spyOn(component['vecServ'], 'deleteVectorDataset').and.returnValue(throwError(() => new Error()));
      let rowSpy = spyOn(component, 'updateRowCount');
  
      // fake information
      let datasets: VectorDataset[] = [{
        id: 1, slug: 'slug', name: 'name', description: 'desc', refYear: 1998, refProd: 2022, source: '',
        categoryID: 1, datasetLevels: [], geometryType: 'POINT',
      }];
      component.datasets = datasets;
      component.openDataset = datasets[0];
      component.isConfChecked = true;
      fixture.detectChanges();
  
      component.removeDataset();
  
      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).toHaveBeenCalledWith('slug');
      expect(component.datasets).toEqual(datasets);
      expect(rowSpy).not.toHaveBeenCalled();
    });
  });

});
