import { Component, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';

// Bootstrap and Fort Awesome
import { faChevronDown, faEdit, faFilter, faPlus, faTimes, faTrash, faVectorSquare } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces
import { TableHeader } from 'src/app/interfaces/backoffice';
import { VectorCategory, VectorDataset, VectorLevel } from 'src/app/interfaces/geospatial';

// Services
import { VectorService } from 'src/app/serv/rest/geo/vector.service';

/**
 * Backoffice Vetorial Dataset component.
 * 
 * Displays a list of FireLoc vetorial datasets. A single dataset can be created, viewed, edited or deleted.
 * It is also possible to filter the datasets with search terms, by category or geometry type.
 */
@Component({
  selector: 'boff-vetorial',
  templateUrl: './vetorial.component.html',
  styleUrls: ['./vetorial.component.css']
})
export class VetorialComponent implements OnInit {

  // icons
  /**
   * icon for category filtering
   */
  filterIcon = faFilter;
  /**
   * icon for geometry filtering
   */
  geometryIcon = faVectorSquare;
  /**
   * icon for dropdown menus
   */
  dropIcon = faChevronDown;
  /**
   * icon for creating a new dataset
   */
  plusIcon = faPlus;
  /**
   * icon for editing a dataset
   */
  editIcon = faEdit;
  /**
   * icon to delete a dataset
   */
  deleteIcon = faTrash;
  /**
   * icon to close information
   */
  closeIcon = faTimes;

  // data
  /**
   * list of vetorial datasets
   */
  datasets: VectorDataset[] = [];
  /**
   * list of vetorial dataset categories
   */
  categories: VectorCategory[] = [];
  /**
   * list of vetorial dataset geometry types
   */
  geometryTypes: any[] = [
    { name: 'POINT', selected: false },
    { name: 'LINESTRING', selected: false },
    { name: 'POLYGON', selected: false },
    { name: 'MULTIPOINT', selected: false },
    { name: 'MULTILINESTRING', selected: false },
    { name: 'MULTIPOLYGON', selected: false },
  ];

  // dataset search
  /**
   * list of filtered vetorial datasets
   */
  filteredDatasets: VectorDataset[] = [];
  /**
   * list of selected category IDs for data filtering
   */
  selectedCategoriesIDs: number[] = [];
  /**
   * list of selected geomtry types for data filtering
   */
  selectedGeometryTypes: string[] = [];
  /**
   * search terms for data filtering
   */
  searchTerms: string = '';

  // table
  /**
   * list of table headers for table component
   */
  headers: TableHeader[] = [
    { objProperty: 'id', columnLabel: '#' },
    { objProperty: 'name', columnLabel: 'Nome' },
    { objProperty: 'source', columnLabel: 'Fonte' },
    { objProperty: 'refYear', columnLabel: 'Ano Dados' },
    { objProperty: 'refProd', columnLabel: 'Ano Produção' },
  ];

  // Dataset details
  /**
   * flag to determine if a single dataset's information is being displayed 
   */
  isDatasetOpen: boolean = false;
  /**
   * reference to open dataset
   */
  openDataset!: VectorDataset;
  /**
   * list of headers to be displayed when a single dataset is closed
   */
  displayedHeaders: TableHeader[] = this.headers;
  /**
   * list of headers to be displayed when a single dataset is open
   */
  openHeaders: TableHeader[] = this.headers.filter((_, index) => index < 3);

  // pagination
  /**
   * current page of data being displayed
   */
  currentPage: number = 1;
  /**
   * number of rows of data in the table
   */
  rowCount: number = this.datasets.length;

  /**
   * new vetorial dataset form
   */
  newDataForm!: FormGroup;
  /**
   * new vetorial dataset data
   */
  newData!: VectorDataset;

  /**
   * edit vetorial dataset form
   */
  editDataForm!: FormGroup;
  /**
   * reference to open dataset for editing
   */
  editData: VectorDataset = { ...this.openDataset };

  // remove dataset
  /**
   * flag to determine if user has confirmed vetorial dataset removal
   */
  isConfChecked: boolean = false;
  /**
   * flag to determine if user has decided to remove a vetorial dataset
   */
  hasClickedRemove: boolean = false;

  /**
   * Empty constructor for the Backoffice Vetorial component.
   * @param vecServ vector service. See {@link VectorService}.
   * @param modalService Bootstrap modal service
   * @param fb Angular form builder
   */
  constructor(private vecServ: VectorService, private modalService: NgbModal, private fb: FormBuilder) { }

  /**
   * Initializes data and necessary forms (create and edit a vetorial dataset).
   */
  ngOnInit(): void {
    // get data
    this.getDatasets();
    this.getCategories();

    // new data form
    this.newDataForm = this.fb.group({
      slug: ['', [Validators.required, Validators.maxLength(10)]],
      name: ['', [Validators.required, Validators.maxLength(50)]],
      description: ['', [Validators.required, Validators.maxLength(250)]],
      source: ['', [Validators.required, Validators.maxLength(75)]],
      refYear: [null, []],
      refProd: [null, []],
      levels: this.fb.array([]),
    });

    // edit data form
    this.editDataForm = this.fb.group({
      slug: ['', [Validators.required, Validators.maxLength(10)]],
      name: ['', [Validators.required, Validators.maxLength(50)]],
      description: ['', [Validators.required, Validators.maxLength(250)]],
      source: ['', [Validators.required, Validators.maxLength(75)]],
      refYear: [null, []],
      refProd: [null, []],
      levels: this.fb.array([]),
    });
  }

  /**
   * Gets levels from add dataset form
   */
  get newLevels(): FormArray { return <FormArray>this.newDataForm.get('levels'); }

  /**
   * Gets levels from edit dataset form
   */
  get editLevels(): FormArray { return <FormArray>this.editDataForm.get('levels'); }

  /**
   * Pushes new levels to new levels form array
   */
  addNewLevels() { this.newLevels.push(this.createLevelGroup()); }

  /**
   * Pushes new levels to edit levels form array
   */
  addEditLevels() { this.editLevels.push(this.createLevelGroup()); }

  /**
   * Creates levels form group
   * @returns created form group
   */
  createLevelGroup(): FormGroup {
    return this.fb.group({
      levelID: [null, []],
      levelSlug: [null, [Validators.required, Validators.maxLength(15)]],
      levelLevel: [null, [Validators.required]],
      levelName: [null, [Validators.required, Validators.maxLength(50)]],
      levelDescription: [null, [Validators.required, Validators.maxLength(250)]],
    });
  }

  /**
   * Removes new level control from new levels form array
   * @param index index of level control in array
   */
  removeNewLevel(index: number) { this.newLevels.removeAt(index); }

  /**
   * Removes level control from edit levels form array
   * @param index index of level control in array
   */
  removeEditLevel(index: number) { this.editLevels.removeAt(index); }

  /**
   * Gets vetorial datasets from API and updates displayed data
   */
  getDatasets() {
    this.vecServ.getVectorDatasets().subscribe(
      (result: any) => {
        this.getDatasetData(result.data);

        // update values for table and pagination
        this.filteredDatasets = JSON.parse(JSON.stringify(this.datasets));
        this.updateRowCount(this.filteredDatasets.length);
      }, error => { }
    );
  }

  /**
   * Gets vectorial dataset data from API request response
   * @param rawData API response data
   */
  getDatasetData(rawData: any[]) {
    rawData.forEach(v => {
      let newDataset: VectorDataset = {
        id: v.id,
        slug: v.slug,
        name: v.name,
        description: v.description,
        source: v.source,
        refYear: v.refyear,
        refProd: v.refprod,
        geometryType: v.gtype,
        categoryID: v.catid,
        datasetLevels: this.getDatasetLevels(v.dsetlevel),
      };
      this.datasets.push(newDataset);
    });
  }

  /**
   * Gets vetorial levels data from API request response
   * @param rawLevels API response data
   * @returns list of vetorial levels
   */
  getDatasetLevels(rawLevels: any[]): VectorLevel[] {
    let levels: VectorLevel[] = [];
    rawLevels.forEach(l => {
      let newLevel: VectorLevel = {
        id: l.id,
        slug: l.slug,
        name: l.name,
        description: l.description,
        level: l.level
      }
      levels.push(newLevel);
    });
    return levels;
  }

  /**
   * Gets vetor categoris from API
   */
  getCategories() {
    this.vecServ.getVectorCategories().subscribe(
      (result: any) => {
        this.getCategoryData(result.data);
      }, error => { }
    );
  }

  /**
   * Gets vetor categories from API request response
   * @param rawData API response data
   */
  getCategoryData(rawData: any[]) {
    rawData.forEach(c => {
      let newCategory: VectorCategory = {
        id: c.id,
        slug: c.slug,
        name: c.name,
        description: c.description
      };
      this.categories.push(newCategory);
    });
  }

  /**
   * Selects vector category and filter datasets with selected categories.
   * @param catID selected category ID
   */
  selectCategory(catID: number) {
    // reset geometry types filter
    if (this.selectedGeometryTypes.length !== 0) {
      this.selectedGeometryTypes = [];
      this.geometryTypes.forEach(t => t.selected = false);
    }

    let index = this.categories.findIndex(c => { return c.id === catID });
    this.categories[index].selected = !this.categories[index].selected;

    // get selected types for filtering
    this.selectedCategoriesIDs = this.categories.filter(cat => cat.selected).map(cat => cat.id);

    // update data and pagination
    if (this.selectedCategoriesIDs.length === 0)
      this.filteredDatasets = JSON.parse(JSON.stringify(this.datasets));
    else
      this.filteredDatasets = this.datasets.filter(dataset => this.selectedCategoriesIDs.includes(dataset.categoryID));
    this.updateRowCount(this.filteredDatasets.length);
  }

  /**
   * Selects vector geometry type and filter datasets with selected geometry types.
   * @param geoType 
   */
  selectGeometryType(geoType: string) {
    // reset category filter
    if (this.selectedCategoriesIDs.length !== 0) {
      this.selectedCategoriesIDs = [];
      this.categories.forEach(c => c.selected = false);
    }

    let index = this.geometryTypes.findIndex(t => { return t.name === geoType });
    this.geometryTypes[index].selected = !this.geometryTypes[index].selected;

    // if geometry type is in filter, remove it
    if (this.selectedGeometryTypes.includes(geoType))
      this.selectedGeometryTypes.splice(this.selectedGeometryTypes.indexOf(geoType), 1);
    // if geometry type is not in filter, add it
    else this.selectedGeometryTypes.push(geoType);

    // update data and pagination
    if (this.selectedGeometryTypes.length === 0)
      this.filteredDatasets = JSON.parse(JSON.stringify(this.datasets));
    else
      this.filteredDatasets = this.datasets.filter(dataset => this.selectedGeometryTypes.includes(dataset.geometryType));
    this.updateRowCount(this.filteredDatasets.length);
  }

  /**
   * Updates search terms.
   * Searches datasets by name and source in table component. 
   * See {@link TableComponent#filterDataSearchVector} for more information.
   * @param searchTerms new search terms
   */
  searchDatasets(searchTerms: string) {
    // ignore clear search event
    if (typeof (searchTerms) === 'string') this.searchTerms = searchTerms;
  }

  /**
   * Updates row count of filtered data for pagination
   * @param rows number of rows
   */
  updateRowCount(rows: number) { this.rowCount = rows; }

  /**
   * Updates the current page of displayed data
   * @param page current page
   */
  getPage(page: any) { this.currentPage = page; }

  /**
   * Opens or closes a single dataset's information display.
   * @param datasetID vetorial dataset ID to display or -1 to close
   */
  toggleDatasetView(datasetID: number) {
    // close dataset details
    if (datasetID === -1) {
      this.isDatasetOpen = false;
      this.displayedHeaders = this.headers;
    }
    // open dataset details
    else {
      this.isDatasetOpen = true;
      this.displayedHeaders = this.openHeaders;

      // find dataset with selected dataset ID
      let datasetIndex = this.datasets.findIndex(item => item.id === datasetID);
      this.openDataset = this.datasets[datasetIndex];

      // find dataset category
      let vectorCategoryID = this.openDataset.categoryID;
      let vectorCategoryIndex = this.categories.findIndex(item => item.id === vectorCategoryID);
      this.openDataset.category = this.categories[vectorCategoryIndex];
    }
  }

  /**
   * Opens modals to create, update or delete a dataset. Initializes the necessary data before opening a modal.
   * @param content modal content to display
   * @param modalType type of modal to open. Can be 'new', 'edit' or 'delete'
   */
  open(content: any, modalType: string) {
    // initialize according to modal
    switch (modalType) {
      case 'new':
        // initialize values
        this.newDataForm.reset();
        this.newDataForm.setControl('levels', this.fb.array([]));
        this.initNewData();
        break;
      case 'edit':
        // initialize values
        this.editDataForm.reset();
        this.editDataForm.setControl('levels', this.fb.array([]));
        this.initEditData();
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
   * Initializes new dataset data
   */
  initNewData() {
    this.newData = {
      id: -1,
      slug: '',
      name: '',
      description: '',
      refYear: null,
      refProd: null,
      source: '',
      categoryID: -1,
      datasetLevels: [],
      geometryType: this.geometryTypes[0].name,
      category: this.categories[0],
    };
  }

  /**
   * Initializes values to update dataset
   */
  initEditData() {
    this.editData = { ...this.openDataset };
    this.editDataForm.patchValue({
      slug: this.editData.slug,
      name: this.editData.name,
      description: this.editData.description,
      source: this.editData.source,
      refYear: this.editData.refYear,
      refProd: this.editData.refProd,
    });

    // initialize series
    for (let index = 0; index < this.editData.datasetLevels.length; index++) {
      this.editLevels.push(this.createLevelGroup());

      // set initial value in form
      let control = this.editLevels.controls[index];
      control.setValue({
        levelID: this.editData.datasetLevels[index].id,
        levelSlug: this.editData.datasetLevels[index].slug,
        levelLevel: this.editData.datasetLevels[index].level,
        levelName: this.editData.datasetLevels[index].name,
        levelDescription: this.editData.datasetLevels[index].description,
      });
    };
  }

  /**
   * Updates new data information from create input form
   * @param value updated value
   * @param field dataset property to update
   */
  updateNewDataField<K extends keyof VectorDataset>(value: VectorDataset[K], field: K) { this.newData[field] = value; }

  /**
   * Updates edit data information from edit input form
   * @param value updated value
   * @param field dataset property to update
   */
  updateEditDataField<K extends keyof VectorDataset>(value: VectorDataset[K], field: K) { this.editData[field] = value; }

  /**
   * Creates a new vetorial dataset with the API if new data form is valid.
   */
  createNewDataset() {
    // check if form is valid
    if (this.newDataForm.valid) {
      // create request data
      let requestData: any = {
        slug: this.newData.slug,
        name: this.newData.name,
        description: this.newData.description,
        source: this.newData.source,
        catid: this.newData.category?.slug,
        gtype: this.newData.geometryType,
      }

      // add optional data if it exists
      if (this.newData.refProd !== null) requestData.refprod = this.newData.refProd;
      if (this.newData.refYear !== null) requestData.refyear = this.newData.refYear;

      //console.log(requestData);
      this.vecServ.addVectorDataset(requestData).subscribe(
        (resultDataset: any) => {
          // get data
          this.getDatasetData([resultDataset]);

          // create levels
          let requestLevels: any[] = [];

          // get new levels values
          for (let index = 0; index < this.newLevels.controls.length; index++) {
            let control = this.newLevels.controls[index];
            let newLevelRequest = {
              slug: control.get('levelSlug')?.value,
              name: control.get('levelName')?.value,
              description: control.get('levelDescription')?.value,
              level: control.get('levelLevel')?.value,
              dsetid: resultDataset.slug,
            }
            requestLevels.push(newLevelRequest);
          }

          // create levels with API requests
          requestLevels.forEach(rl => {
            this.vecServ.addVectorLevel(rl).subscribe(
              (resultLevel: any) => {
                // create level from response
                let newLevel: VectorLevel = {
                  id: resultLevel.id,
                  slug: resultLevel.slug,
                  name: resultLevel.name,
                  description: resultLevel.description,
                  level: resultLevel.level
                }

                // get dataset reference
                let dataIndex = this.datasets.findIndex(dataset => dataset.id === resultDataset.id);
                let datasetRef = this.datasets[dataIndex];

                // add level to dataset
                datasetRef.datasetLevels.push(newLevel);
              }, error => { }
            );
          });

          // update table and pagination
          this.filteredDatasets = JSON.parse(JSON.stringify(this.datasets));
          this.updateRowCount(this.filteredDatasets.length);
        }, error => { }
      );
    }

    // close
    this.modalService.dismissAll();
  }

  /**
   * Updates a vetorial dataset if edit data form is valid.
   */
  updateDataset() {
    // check if form is valid
    if (this.editDataForm.valid) {
      // create request data
      let requestData: any = {
        slug: this.editData.slug,
        name: this.editData.name,
        description: this.editData.description,
        source: this.editData.source,
        catid: this.editData.category?.slug,
        gtype: this.editData.geometryType,
        refprod: Number.isNaN(this.editData.refProd) ? null : this.editData.refProd,
        refyear: Number.isNaN(this.editData.refYear) ? null : this.editData.refYear,
      }

      this.vecServ.updateVectorDataset(this.openDataset.slug, requestData).subscribe(
        (result: any) => {
          // get dataset reference
          let dataIndex = this.datasets.findIndex(dataset => dataset.id === this.openDataset.id);
          let datasetRef = this.datasets[dataIndex];

          // update data
          datasetRef.slug = result.slug;
          datasetRef.name = result.name;
          datasetRef.description = result.description;
          datasetRef.source = result.source;
          datasetRef.datasetLevels = this.getDatasetLevels(result.dsetlevel);
          datasetRef.refProd = result.refprod;
          datasetRef.refYear = result.refyear;
          datasetRef.categoryID = result.catid;
          datasetRef.geometryType = result.gtype;

          let vectorCategoryIndex = this.categories.findIndex(item => item.id === datasetRef.categoryID);
          datasetRef.category = this.categories[vectorCategoryIndex];

          // update table
          this.filteredDatasets = JSON.parse(JSON.stringify(this.datasets));

          // ---- update dataset levels
          let originalLevelIDs: any[] = datasetRef.datasetLevels.map(level => level.id);

          // get new levels values
          for (let index = 0; index < this.editLevels.controls.length; index++) {
            let control = this.editLevels.controls[index];
            let id = control.get('levelID')?.value

            // if level control id is null, add new level to dataset 
            if (id === null) {
              let newLevelRequest = {
                slug: control.get('levelSlug')?.value,
                name: control.get('levelName')?.value,
                description: control.get('levelDescription')?.value,
                level: control.get('levelLevel')?.value,
                dsetid: datasetRef.slug,
              };

              this.vecServ.addVectorLevel(newLevelRequest).subscribe(
                (resultLevel: any) => {
                  // create level from response
                  let newLevel: VectorLevel = {
                    id: resultLevel.id,
                    slug: resultLevel.slug,
                    name: resultLevel.name,
                    description: resultLevel.description,
                    level: resultLevel.level
                  }
                  // add level to dataset
                  datasetRef.datasetLevels.push(newLevel);
                }, error => { }
              );
            }
            // if level control id is in original ids, edit level in dataset
            else if (originalLevelIDs.includes(id)) {
              originalLevelIDs.splice(originalLevelIDs.indexOf(id), 1);

              // get level slug
              let levelIndex = datasetRef.datasetLevels.findIndex(l => l.id === id);
              let originalSlug = datasetRef.datasetLevels[levelIndex].slug;

              let editLevelRequest = {
                slug: control.get('levelSlug')?.value,
                name: control.get('levelName')?.value,
                description: control.get('levelDescription')?.value,
                level: control.get('levelLevel')?.value,
              };
              this.vecServ.updateVectorLevel(originalSlug, editLevelRequest).subscribe(
                (resultLevel: any) => {
                  // create level from response
                  let updatedLevel: VectorLevel = {
                    id: resultLevel.id,
                    slug: resultLevel.slug,
                    name: resultLevel.name,
                    description: resultLevel.description,
                    level: resultLevel.level
                  }

                  // update level on dataset
                  datasetRef.datasetLevels[levelIndex] = updatedLevel;
                }, error => { }
              );
            }
          }

          // if there are still ids in original ids array, send delete requests for each
          if (originalLevelIDs.length !== 0) {
            originalLevelIDs.forEach(id => {
              // get level slug
              let levelIndex = datasetRef.datasetLevels.findIndex(l => l.id === id);
              let slug = datasetRef.datasetLevels[levelIndex].slug;

              // request to delete
              this.vecServ.deleteVectorLevel(slug).subscribe(
                (resultLevel: any) => {
                  // delete level in dataset
                  datasetRef.datasetLevels.splice(levelIndex, 1);
                }, error => { }
              );
            });
          }
        }, error => { }
      );
    }

    // close    
    this.modalService.dismissAll();
  }

  /**
   * Checks if the user has confirmed the removal of a vetorial dataset.
   * 
   * If there is confirmation, delete a vetorial dataset with the API and update the displayed data.
   */
  removeDataset() {
    this.hasClickedRemove = true;
    // without checked confirmation, show error
    if (this.isConfChecked) {
      // remove dataset with API
      this.vecServ.deleteVectorDataset(this.openDataset.slug).subscribe(
        (result: any) => {
          // close display
          this.isDatasetOpen = false;
          this.displayedHeaders = this.headers;

          // remove dataset from list
          let datasetIndex = this.datasets.findIndex(item => item.id === this.openDataset.id);
          this.datasets.splice(datasetIndex, 1);

          // update dataset table and pagination
          this.filteredDatasets = JSON.parse(JSON.stringify(this.datasets));
          this.updateRowCount(this.filteredDatasets.length);
        }, error => { }
      );

      // close
      this.modalService.dismissAll();
    }
  }

}
