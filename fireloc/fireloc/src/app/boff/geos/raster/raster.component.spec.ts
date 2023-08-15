import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { of, throwError } from 'rxjs';
import { FeatModule } from 'src/app/feat/feat.module';
import { RasterDataset, RasterType } from 'src/app/interfaces/geospatial';

import { RasterComponent } from './raster.component';

describe('TS13 Backoffice RasterComponent', () => {
  let component: RasterComponent;
  let fixture: ComponentFixture<RasterComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [RasterComponent],
      imports: [
        HttpClientTestingModule,
        FeatModule,
        FontAwesomeModule,
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(RasterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T13.1 should create', () => { expect(component).toBeTruthy(); });

  it('T13.2 should get datasets from API', () => {
    // setup
    let getSpy = spyOn(component, 'getDatasets').and.callThrough();
    let getAPISpy = spyOn(component['rasterServ'], 'getRasterDatasets')
      .and.returnValue(of({
        data: [{
          id: 1, slug: '', name: '', description: '', refyear: null, refprod: null, source: '', idtype: 1
        }]
      }));
    let dataSpy = spyOn(component, 'getDatasetData').and.callThrough();
    let rowSpy = spyOn(component, 'updateRowCount');

    component.getDatasets();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).toHaveBeenCalled();
    expect(rowSpy).toHaveBeenCalled();
    expect(component.datasets.length).not.toBe(0);
  });

  it('T13.3 should handle error from getting datasets from API', () => {
    // setup
    let getSpy = spyOn(component, 'getDatasets').and.callThrough();
    let getAPISpy = spyOn(component['rasterServ'], 'getRasterDatasets')
      .and.returnValue(throwError(() => new Error()));
    let dataSpy = spyOn(component, 'getDatasetData').and.callThrough();
    let rowSpy = spyOn(component, 'updateRowCount');

    component.getDatasets();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).not.toHaveBeenCalled();
    expect(rowSpy).not.toHaveBeenCalled();
    expect(component.datasets.length).toBe(0);
  });

  it('T13.4 should get dataset types from API', () => {
    // setup
    let getSpy = spyOn(component, 'getRasterTypes').and.callThrough();
    let getAPISpy = spyOn(component['rasterServ'], 'getRasterTypes')
      .and.returnValue(of({ data: [{ id: 1, slug: '', name: '', description: '' }] }));

    component.getRasterTypes();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(component.types.length).not.toBe(0);
  });

  it('T13.5 should handle error from getting dataset types from API', () => {
    // setup
    let getSpy = spyOn(component, 'getRasterTypes').and.callThrough();
    let getAPISpy = spyOn(component['rasterServ'], 'getRasterTypes')
      .and.returnValue(throwError(() => new Error()));
    let rowSpy = spyOn(component, 'updateRowCount');

    component.getRasterTypes();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(component.types.length).toBe(0);
  });

  it('T13.6 should filter datasets by type', () => {
    // fake data
    let types: RasterType[] = [
      { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
      { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
    ];
    let datasets: RasterDataset[] = [{
      id: 1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '', typeID: 1
    }];
    component.types = types;
    component.datasets = datasets;
    fixture.detectChanges();

    // spies
    let selectSpy = spyOn(component, 'selectType').and.callThrough();

    component.selectType(1); // id:1 -> selected true
    component.selectType(1); // id:1 -> selected false

    // expectations
    expect(selectSpy).toHaveBeenCalledWith(1);
    expect(component.types[0].selected).toBeFalse();
    expect(component.selectedTypeIDs).toEqual([]);
  });

  it('T13.7 should update search terms', () => {
    // spies
    let searchSpy = spyOn(component, 'searchDatasets').and.callThrough();

    component.searchDatasets(null as unknown as string);
    component.searchDatasets('search');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('search');
    expect(component.searchTerms).toEqual('search');
  });

  it('T13.8 should update data row count for pagination', () => {
    // setup
    let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();
    component.updateRowCount(10);
    // expectations
    expect(rowSpy).toHaveBeenCalledOnceWith(10);
    expect(component.rowCount).toBe(10);
  });

  it('T13.9 should get current page for table component', () => {
    // setup
    let pageSpy = spyOn(component, 'getPage').and.callThrough();
    component.getPage(5);
    // expectations
    expect(pageSpy).toHaveBeenCalledOnceWith(5);
    expect(component.currentPage).toBe(5);
  });

  it('T13.10 should open dataset details view', () => {
    // fake data
    let datasets: RasterDataset[] = [{
      id: 1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '', typeID: 1
    }];
    let types: RasterType[] = [
      { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
      { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
    ];
    component.datasets = datasets;
    component.types = types;
    fixture.detectChanges();

    // spies
    let datasetViewSpy = spyOn(component, 'toggleDatasetView').and.callThrough();

    component.toggleDatasetView(1);

    // expectations
    expect(datasetViewSpy).toHaveBeenCalledWith(1);
    expect(component.isDatasetOpen).toBeTrue();
    expect(component.displayedHeaders).toEqual(component.openHeaders);
    expect(component.openDataset).toEqual(datasets[0]);
    expect(component.openDataset.type).toEqual(types[0]);
  });

  it('T13.11 should close dataset details view', () => {
    // fake data
    let datasets: RasterDataset[] = [{
      id: 1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '', typeID: 1
    }];
    let types: RasterType[] = [
      { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
      { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
    ];
    component.datasets = datasets;
    component.types = types;
    fixture.detectChanges();

    // spies
    let datasetViewSpy = spyOn(component, 'toggleDatasetView').and.callThrough();

    component.toggleDatasetView(-1);

    // expectations
    expect(datasetViewSpy).toHaveBeenCalledWith(-1);
    expect(component.isDatasetOpen).toBeFalse();
    expect(component.displayedHeaders).toEqual(component.headers);
  });

  describe('TS13.1 should open modal according to type', () => {
    it('T13.1.1 type: new', () => {
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

    it('T13.1.2 type: edit', () => {
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

    it('T13.1.3 type: delete', () => {
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

  it('T13.12 should initialize values for new dataset form', () => {
    // fake data
    let types: RasterType[] = [
      { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
      { id: 2, name: 'name2', slug: 'slug2', description: 'desc2', selected: false },
    ];
    component.types = types;
    fixture.detectChanges();

    // spies
    let initSpy = spyOn(component, 'initNewData').and.callThrough();

    component.initNewData();

    // expectations
    expect(initSpy).toHaveBeenCalledWith();
    expect(component.newData).toEqual({
      id: -1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '', typeID: -1, type: types[0],
    });
  });

  it('T13.13 should initialize data for edit dataset form', () => {
    // fake data
    let openDataset: RasterDataset = {
      id: 0,
      slug: '',
      name: '',
      description: '',
      refYear: null,
      refProd: null,
      source: '',
      typeID: 0
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

  it('T13.14 should update new dataset property when form changes', () => {
    // fake data
    let newData: RasterDataset = {
      id: -1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '', typeID: -1
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

  it('T13.15 should update edit dataset property when form changes', () => {
    // spies
    let updateSpy = spyOn(component, 'updateEditDataField').and.callThrough();
    component.updateEditDataField('newName', 'name');
    // expectations
    expect(updateSpy).toHaveBeenCalledWith('newName', 'name');
    expect(component.editData.name).toEqual('newName');
  });

  it('T13.16 should not create a new dataset if new data form is invalid', () => {
    // spies
    let createSpy = spyOn(component, 'createNewDataset').and.callThrough();
    let addAPISpy = spyOn(component['rasterServ'], 'addRasterDataset');
    let getInfoSpy = spyOn(component, 'getDatasetData');
    let rowSpy = spyOn(component, 'updateRowCount');

    component.createNewDataset();

    // expectations
    expect(createSpy).toHaveBeenCalled();
    expect(addAPISpy).not.toHaveBeenCalled();
    expect(getInfoSpy).not.toHaveBeenCalled();
    expect(rowSpy).not.toHaveBeenCalled();
  });

  it('T13.17 should create a new dataset (no optional data)', () => {
    // spies
    let createSpy = spyOn(component, 'createNewDataset').and.callThrough();
    let addAPISpy = spyOn(component['rasterServ'], 'addRasterDataset').and.returnValue(of({
      data: [{
        id: 1, slug: '', name: '', description: '', refyear: null, refprod: null, source: '', idtype: 1
      }]
    }));
    let getInfoSpy = spyOn(component, 'getDatasetData');
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake new dataset information
    component.newData = {
      id: -1, slug: 'slug', name: 'name', description: 'desc',
      refYear: null, refProd: null, source: 'source', typeID: -1,
    };
    component.newDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
    fixture.detectChanges();

    component.createNewDataset();

    // expectations
    expect(createSpy).toHaveBeenCalledWith();
    expect(addAPISpy).toHaveBeenCalled();
    expect(getInfoSpy).toHaveBeenCalled();
    expect(rowSpy).toHaveBeenCalled();
  });

  it('T13.18 should create a new dataset (optional data)', () => {
    // spies
    let createSpy = spyOn(component, 'createNewDataset').and.callThrough();
    let addAPISpy = spyOn(component['rasterServ'], 'addRasterDataset').and.returnValue(of({
      data: [{
        id: 1, slug: '', name: '', description: '', refyear: null, refprod: null, source: '', idtype: 1
      }]
    }));
    let getInfoSpy = spyOn(component, 'getDatasetData');
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake new dataset information
    component.newData = {
      id: -1, slug: 'slug', name: 'name', description: 'desc',
      refYear: 1998, refProd: 2022, source: 'source', typeID: -1,
      type: { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
    };
    component.newDataForm.patchValue(
      { slug: 'slug', name: 'name', description: 'desc', source: 'source', refYear: 1998, refProd: 2022 }
    );
    fixture.detectChanges();

    component.createNewDataset();

    // expectations
    expect(createSpy).toHaveBeenCalledWith();
    expect(addAPISpy).toHaveBeenCalled();
    expect(getInfoSpy).toHaveBeenCalled();
    expect(rowSpy).toHaveBeenCalled();
  });

  it('T13.19 should handle error on creating a new dataset', () => {
    // spies
    let createSpy = spyOn(component, 'createNewDataset').and.callThrough();
    let addAPISpy = spyOn(component['rasterServ'], 'addRasterDataset').and.returnValue(throwError(() => new Error()));
    let getInfoSpy = spyOn(component, 'getDatasetData');
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake new dataset information
    component.newData = {
      id: -1, slug: 'slug', name: 'name', description: 'desc',
      refYear: 1998, refProd: 2022, source: 'source', typeID: -1,
      type: { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
    };
    component.newDataForm.patchValue(
      { slug: 'slug', name: 'name', description: 'desc', source: 'source', refYear: 1998, refProd: 2022 }
    );
    fixture.detectChanges();

    component.createNewDataset();

    // expectations
    expect(createSpy).toHaveBeenCalledWith();
    expect(addAPISpy).toHaveBeenCalled();
    expect(getInfoSpy).not.toHaveBeenCalled();
    expect(rowSpy).not.toHaveBeenCalled();
  });

  it('T13.20 should not edit a dataset if edit data form is invalid', () => {
    // spies
    let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
    let updateAPISpy = spyOn(component['rasterServ'], 'updateRasterDataset');

    component.updateDataset();

    // expectations
    expect(updateSpy).toHaveBeenCalled();
    expect(updateAPISpy).not.toHaveBeenCalled();
  });

  it('T13.21 should update a dataset (no optional data)', () => {
    // spies
    let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
    let updateAPISpy = spyOn(component['rasterServ'], 'updateRasterDataset').and.returnValue(of({
      data: [{
        id: 1, slug: '', name: '', description: '', refyear: null, refprod: null, source: '', idtype: 1
      }]
    }));

    // fake dataset
    let datasets: RasterDataset[] = [{
      id: 1, slug: '', name: '', description: '', refYear: null, refProd: null, source: '', typeID: 1
    }];
    component.datasets = datasets;  
    component.openDataset = datasets[0];

    // fake edit dataset information
    component.editData = {
      id: -1, slug: 'slug', name: 'name', description: 'desc',
      refYear: NaN, refProd: NaN, source: 'source', typeID: -1,
    };
    component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
    fixture.detectChanges();

    component.updateDataset();

    // expectations
    expect(updateSpy).toHaveBeenCalledWith();
    expect(updateAPISpy).toHaveBeenCalled();
  });

  it('T13.22 should update a dataset (optional data)', () => {
    // spies
    let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
    let updateAPISpy = spyOn(component['rasterServ'], 'updateRasterDataset').and.returnValue(of({
      data: [{
        id: 1, slug: '', name: '', description: '', refyear: null, refprod: null, source: '', idtype: 1
      }]
    }));

    // fake dataset
    let datasets: RasterDataset[] = [{
      id: 1, slug: '', name: '', description: '', refYear: 1998, refProd: 2022, source: '', typeID: 1
    }];
    component.datasets = datasets;  
    component.openDataset = datasets[0];

    // fake edit dataset information
    component.editData = {
      id: 1, slug: 'slug', name: 'name', description: 'desc',
      refYear: 1998, refProd: 2022, source: 'source', typeID: 1,
      type: { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
    };
    component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
    fixture.detectChanges();

    component.updateDataset();

    // expectations
    expect(updateSpy).toHaveBeenCalledWith();
    expect(updateAPISpy).toHaveBeenCalled();
  });

  it('T13.23 should handle error on editing a new dataset', () => {
    // spies
    let updateSpy = spyOn(component, 'updateDataset').and.callThrough();
    let updateAPISpy = spyOn(component['rasterServ'], 'updateRasterDataset').and.returnValue(throwError(() => new Error()));

    // fake dataset
    let datasets: RasterDataset[] = [{
      id: 1, slug: '', name: '', description: '', refYear: 1998, refProd: 2022, source: '', typeID: 1
    }];
    component.datasets = datasets;  
    component.openDataset = datasets[0];

    // fake edit dataset information
    component.editData = {
      id: 1, slug: 'slug', name: 'name', description: 'desc',
      refYear: 1998, refProd: 2022, source: 'source', typeID: 1,
      type: { id: 1, name: 'name1', slug: 'slug1', description: 'desc1', selected: false },
    };
    component.editDataForm.patchValue({ slug: 'slug', name: 'name', description: 'desc', source: 'source' });
    fixture.detectChanges();

    component.updateDataset();

    // expectations
    expect(updateSpy).toHaveBeenCalledWith();
    expect(updateAPISpy).toHaveBeenCalled();
  });

  it('T13.24 should not delete dataset without confirmation', () => {
    // spies
    let deleteSpy = spyOn(component, 'removeDataset').and.callThrough();
    let deleteAPISpy = spyOn(component['rasterServ'], 'deleteRasterDataset');

    component.removeDataset();

    // expectations
    expect(deleteSpy).toHaveBeenCalledWith();
    expect(deleteAPISpy).not.toHaveBeenCalled();
  });

  it('T13.25 should delete dataset information if there was confirmation', () => {
    // spies
    let deleteSpy = spyOn(component, 'removeDataset').and.callThrough();
    let deleteAPISpy = spyOn(component['rasterServ'], 'deleteRasterDataset').and.returnValue(of({}));
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake information
    let datasets: RasterDataset[] = [{
      id: 1, slug: 'slug', name: '', description: '', refYear: null, refProd: null, source: '', typeID: 1
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
    expect(rowSpy).toHaveBeenCalledWith(0);
  });

  it('T13.26 should handle error on deleting dataset information if there was confirmation', () => {
    // spies
    let deleteSpy = spyOn(component, 'removeDataset').and.callThrough();
    let deleteAPISpy = spyOn(component['rasterServ'], 'deleteRasterDataset').and.returnValue(throwError(() => new Error()));
    let rowSpy = spyOn(component, 'updateRowCount');

    // fake information
    let datasets: RasterDataset[] = [{
      id: 1, slug: 'slug', name: '', description: '', refYear: null, refProd: null, source: '', typeID: 1
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
