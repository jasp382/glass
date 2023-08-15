import { Component, OnInit } from '@angular/core';

// Font Awesome
import { faFilter, faChevronDown, faPlus, faEdit, faTrash, faTimes } from '@fortawesome/free-solid-svg-icons';

// Bootstrap
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces
import { RasterDataset, RasterType } from 'src/app/interfaces/geospatial';
import { TableHeader } from 'src/app/interfaces/backoffice';

// Services
import { RasterService } from 'src/app/serv/rest/geo/raster.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';

/**
 * Backoffice Raster Dataset component.
 * 
 * Displays a list of FireLoc raster datasets. A single dataset can be created, viewed, edited or deleted.
 * It is also possible to filter the datasets with search terms or by raster type.
 */
@Component({
  selector: 'boff-raster',
  templateUrl: './raster.component.html',
  styleUrls: ['./raster.component.css']
})
export class RasterComponent implements OnInit {

  // icons
  /**
   * icon for type filtering
   */
  typeIcon = faFilter;
  /**
   * icon for dropdown menus
   */
  dropIcon = faChevronDown;
  /**
   * icon for dataset creation
   */
  plusIcon = faPlus;
  /**
   * icon for dataset edition
   */
  editIcon = faEdit;
  /**
   * icon for dataset deletion
   */
  deleteIcon = faTrash;
  /**
   * icon to close information
   */
  closeIcon = faTimes;

  /**
   * list of raster datasets
   */
  datasets: RasterDataset[] = [];

  // dataset search
  /**
   * list of raster dataset types
   */
  types: RasterType[] = [];
  /**
   * list of filtered raster datasets
   */
  filteredDatasets: RasterDataset[] = [];
  /**
   * list of selected raster type IDs for data filtering
   */
  selectedTypeIDs: number[] = [];
  /**
   * search terms for data filtering
   */
  searchTerms: string = '';

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
  openDataset!: RasterDataset;
  /**
   * list of headers to be displayed when a single dataset is closed
   */
  displayedHeaders: TableHeader[] = this.headers;
  /**
   * list of headers to be displayed when a single dataset is open
   */
  openHeaders: TableHeader[] = this.headers.filter((_, index) => index < 3);

  // create new raster dataset
  /**
   * new raster dataset form
   */
  newDataForm!: FormGroup;
  /**
   * new raster dataset data
   */
  newData!: RasterDataset;

  // edit dataset
  /**
   * edit raster dataset form
   */
  editDataForm!: FormGroup;
  /**
   * reference to open dataset for editing
   */
  editData: RasterDataset = { ...this.openDataset };

  // remove dataset
  /**
  * flag to determine if user has confirmed raster dataset removal
  */
  isConfChecked: boolean = false;
  /**
   * flag to determine if user has decided to remove a raster dataset
   */
  hasClickedRemove: boolean = false;

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
   * Empty constructor for the Backoffice Raster component.
   * @param rasterServ raster service. See {@link RasterService}.
   * @param modalService Bootstrap modal service
   */
  constructor(private rasterServ: RasterService, private modalService: NgbModal) { }

  /**
   * Initializes data and necessary forms (create and edit a raster dataset).
   */
  ngOnInit(): void {
    // get data
    this.getDatasets();
    this.getRasterTypes();

    // new data form
    this.newDataForm = new FormGroup({
      slug: new FormControl('', [Validators.required, Validators.maxLength(10)]),
      name: new FormControl('', [Validators.required, Validators.maxLength(50)]),
      description: new FormControl('', [Validators.required, Validators.maxLength(250)]),
      source: new FormControl('', [Validators.required, Validators.maxLength(75)]),
      refYear: new FormControl(null, []),
      refProd: new FormControl(null, []),
    });

    // edit data form
    this.editDataForm = new FormGroup({
      slug: new FormControl('', [Validators.required, Validators.maxLength(10)]),
      name: new FormControl('', [Validators.required, Validators.maxLength(50)]),
      description: new FormControl('', [Validators.required, Validators.maxLength(250)]),
      source: new FormControl('', [Validators.required, Validators.maxLength(75)]),
      refYear: new FormControl(null, []),
      refProd: new FormControl(null, []),
    });
  }

  /**
   * Gets raster datasets from API
   */
  getDatasets() {
    this.rasterServ.getRasterDatasets().subscribe(
      (result: any) => {
        this.getDatasetData(result.data);
        // update values for table and pagination
        this.filteredDatasets = JSON.parse(JSON.stringify(this.datasets));
        this.updateRowCount(this.filteredDatasets.length);
      }, error => { }
    );
  }

  /**
   * Gets raster dataset data from API request response
   * @param rawData API response data
   */
  getDatasetData(rawData: any[]) {
    rawData.forEach(r => {
      let newDataset: RasterDataset = {
        id: r.id,
        slug: r.slug,
        name: r.name,
        description: r.description,
        refYear: r.refyear,
        refProd: r.refprod,
        source: r.source,
        typeID: r.idtype
      };
      this.datasets.push(newDataset);
    });
  }

  /**
   * Gets raster dataset types data from API.
   */
  getRasterTypes() {
    this.rasterServ.getRasterTypes().subscribe(
      (result: any) => {
        // get raster types data
        result.data.forEach((t: any) => {
          let newType: RasterType = {
            id: t.id,
            slug: t.slug,
            name: t.name,
            description: t.description,
          }
          this.types.push(newType);
        });
      }, error => { }
    );
  }

  /**
   * Selects raster type and filter datasets with selected type.
   * @param typeID selected type ID
   */
  selectType(typeID: number) {
    let index = this.types.findIndex(t => { return t.id === typeID });
    this.types[index].selected = !this.types[index].selected;

    // get selected types for filtering
    this.selectedTypeIDs = this.types.filter(type => type.selected).map(type => type.id);

    // update data and pagination
    if (this.selectedTypeIDs.length === 0)
      this.filteredDatasets = JSON.parse(JSON.stringify(this.datasets));
    else this.filteredDatasets = this.datasets.filter(dataset => this.selectedTypeIDs.includes(dataset.typeID));

    this.updateRowCount(this.filteredDatasets.length);
  }

  /**
   * Updates search terms.
   * Searches datasets by name and source in table component. 
   * See {@link TableComponent#filterDataSearchRaster} for more information.
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
   * @param datasetID raster dataset ID to display or -1 to close
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

      // find dataset type
      let rasterTypeID = this.openDataset.typeID;
      let rasterTypeIndex = this.types.findIndex(item => item.id === rasterTypeID);
      this.openDataset.type = this.types[rasterTypeIndex];
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
        this.initNewData();
        break;
      case 'edit':
        // initialize values
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
      typeID: -1,
      type: this.types[0],
    };
  }

  /**
   * Initializes values to update dataset
   */
  initEditData() {
    this.editData = { ...this.openDataset };
    this.editDataForm.setValue({
      slug: this.editData.slug,
      name: this.editData.name,
      description: this.editData.description,
      source: this.editData.source,
      refYear: this.editData.refYear,
      refProd: this.editData.refProd,
    });
  }

  /**
   * Updates new data information from create input form
   * @param value updated value
   * @param field dataset property to update
   */
  updateNewDataField<K extends keyof RasterDataset>(value: RasterDataset[K], field: K) { this.newData[field] = value; }

  /**
   * Updates edit data information from edit input form
   * @param value updated value
   * @param field dataset property to update
   */
  updateEditDataField<K extends keyof RasterDataset>(value: RasterDataset[K], field: K) { this.editData[field] = value; }

  /**
   * Creates a new raster dataset with the API if new data form is valid.
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
        idtype: this.newData.type?.slug,
      }

      // add optional data if it exists
      if (this.newData.refProd !== null) requestData.refprod = this.newData.refProd;
      if (this.newData.refYear !== null) requestData.refyear = this.newData.refYear;

      //console.log(requestData);
      this.rasterServ.addRasterDataset(requestData).subscribe(
        (result: any) => {
          // get data
          this.getDatasetData([result]);

          // update table and pagination
          this.filteredDatasets = JSON.parse(JSON.stringify(this.datasets));
          this.updateRowCount(this.filteredDatasets.length);
        }, error => { }
      );
    }

    // close and reset
    this.newDataForm.reset();
    this.modalService.dismissAll();
  }

  /**
   * Updates a raster dataset if edit data form is valid.
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
        idtype: this.editData.type?.slug,
        refprod: Number.isNaN(this.editData.refProd) ? null : this.editData.refProd,
        refyear: Number.isNaN(this.editData.refYear) ? null : this.editData.refYear,
      }
      //console.log(requestData);

      this.rasterServ.updateRasterDataset(this.openDataset.slug, requestData).subscribe(
        (result: any) => {
          //console.log(result);

          // get dataset reference
          let dataIndex = this.datasets.findIndex(dataset => dataset.id === this.openDataset.id);
          let datasetRef = this.datasets[dataIndex];

          // update data
          datasetRef.slug = result.slug;
          datasetRef.name = result.name;
          datasetRef.description = result.description;
          datasetRef.source = result.source;
          datasetRef.refProd = result.refprod;
          datasetRef.refYear = result.refyear;
          datasetRef.typeID = result.idtype;
          datasetRef.type = this.editData.type;

          // update table
          this.filteredDatasets = JSON.parse(JSON.stringify(this.datasets));
        },
        error => { /* console.error("error updating dataset on backoffice raster: ", error);  */ }

      );
    }

    // close and reset
    this.editDataForm.reset();
    this.modalService.dismissAll();
  }

  /**
   * Checks if the user has confirmed the removal of a raster dataset.
   * 
   * If there is confirmation, delete a raster dataset with the API and update the displayed data.
   */
  removeDataset() {
    this.hasClickedRemove = true;
    // without checked confirmation, show error
    if (this.isConfChecked) {
      // remove dataset with API
      this.rasterServ.deleteRasterDataset(this.openDataset.slug).subscribe(
        (result: any) => {
          // close user display
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
