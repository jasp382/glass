import { Component, OnInit } from '@angular/core';
import { faChevronDown, faChevronUp, faTimes, faTrash } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Interfaces
import { TableHeader } from 'src/app/interfaces/backoffice';
import { SentinelImg } from 'src/app/interfaces/geospatial';

// Services
import { SatelliteService } from 'src/app/serv/rest/geo/satellite.service';

/**
 * Backoffice Satellite Dataset component.
 * 
 * Displays a list of FireLoc satellite datasets. A single dataset can be viewed or deleted.
 * It is also possible to filter the datasets with search terms.
 */
@Component({
  selector: 'boff-satellite',
  templateUrl: './satellite.component.html',
  styleUrls: ['./satellite.component.css']
})
export class SatelliteComponent implements OnInit {

  // icons
  /**
   * icon for deleting a dataset
   */
  deleteIcon = faTrash;
  /**
   * icon to open dropdown menus
   */
  downIcon = faChevronDown;
  /**
   * icon to close dropdown menus
   */
  upIcon = faChevronUp;
  /**
   * icon to close information
   */
  closeIcon = faTimes;

  /**
   * list of satellite datasets
   */
  datasets: SentinelImg[] = [];

  /**
   * search terms for dataset filtering
   */
  searchTerms: string = '';

  // table
  /**
   * list of table headers for table component
   */
  headers: TableHeader[] = [
    { objProperty: 'id', columnLabel: '#' },
    { objProperty: 'summary', columnLabel: 'Resumo' },
    { objProperty: 'title', columnLabel: 'Título' },
  ];
  /**
   * list of headers to be displayed when a single dataset is closed
   */
  displayedHeaders: TableHeader[] = this.headers;

  // Dataset details
  /**
   * flag to determine if a single dataset's information is being displayed 
   */
  isDatasetOpen: boolean = false;
  /**
   * reference to open dataset
   */
  openDataset!: SentinelImg;
  /**
   * list of headers to be displayed when a single dataset is open
   */
  openHeaders: TableHeader[] = this.headers.filter((_, index) => index < 2);

  // dataset details dropdowns
  /**
   * flag to determine if dataset details section is open
   */
  isDetOpen: boolean = false;
  /**
   * flag to determine if dataset identifiers section is open
   */
  isIDsOpen: boolean = false;
  /**
   * flag to determine if dataset dates section is open
   */
  isDatesOpen: boolean = false;
  /**
   * flag to determine if dataset percentages section is open
   */
  isPercentOpen: boolean = false;
  /**
   * flag to determine if dataset geospatial section is open
   */
  isGeoOpen: boolean = false;
  /**
   * flag to determine if dataset processing section is open
   */
  isProcOpen: boolean = false;
  /**
   * flag to determine if dataset other section is open
   */
  isOtherOpen: boolean = false;

  // pagination
  /**
   * current page of data being displayed
   */
  currentPage: number = 1;
  /**
   * number of rows of data in the table
   */
  rowCount: number = this.datasets.length;

  // remove dataset
  /**
   * flag to determine if user has confirmed satellite dataset removal
   */
  isConfChecked: boolean = false;
  /**
   * flag to determine if user has decided to remove a satellite dataset
   */
  hasClickedRemove: boolean = false;

  /**
   * Empty constructor for the Backoffice Satellite component.
   * @param satServ satellite service. See {@link SatelliteService}.
   * @param modalService Bootstrap modal service.
   */
  constructor(private satServ: SatelliteService, private modalService: NgbModal) { }

  /**
   * Initializes data
   */
  ngOnInit(): void {
    // get data
    this.getDatasets();
  }

  /**
   * Gets satellite datasets from the API and updates the displayed data
   */
  getDatasets() {
    this.satServ.getSatDatasets().subscribe(
      (result: any) => {
        this.getDatasetData(result.data);
        // update values for table and pagination
        this.datasets = JSON.parse(JSON.stringify(this.datasets));
        this.updateRowCount(this.datasets.length);
      }, error => { }
    );
  }

  // get satellite dataset data from API request response
  /**
   * Gets satellite dataset data from API request response.
   * @param rawData API response data
   */
  getDatasetData(rawData: any[]) {
    rawData.forEach(s => {
      let newDataset: SentinelImg = {
        id: s.id,
        identifier: s.identifier,
        dataStripIdentifier: s.datastripidentifier,
        granuleIdentifier: s.granuleidentifier,
        level1CpdiIdentifier: s.level1cpdiidentifier,
        platformIdentifier: s.platformidentifier,
        platformSerialIdentifier: s.platformserialidentifier,
        s2DataTakeId: s.s2datatakeid,
        uuid: s.uuid,
        title: s.title,
        summary: s.summary,
        beginPositionDate: this.processDate(s.beginposition),
        endPositionDate: this.processDate(s.endposition),
        ingestionDate: this.processDate(s.ingestiondate),
        generationDate: this.processDate(s.generationdate),
        cloudCoverPercentage: s.cloudcoverpercentage,
        mediumProbCloudsPercentage: s.mediumprobacloudspercentage,
        highProbCloudsPercentage: s.highprobacloudspercentage,
        vegetationPercentage: s.vegetationpercentage,
        notVegetatedPercentage: s.notvegetatedpercentage,
        waterPercentage: s.waterpercentage,
        unclassifiedPercentage: s.unclassifiedpercentage,
        snowIcePercentage: s.snowicepercentage,
        orbitNumber: s.orbitnumber,
        relativeOrbitNumber: s.relativeorbitnumber,
        orbitDirection: s.orbitdirection,
        geometry: s.geometry,
        illuminationAzimuthAngle: s.illuminationazimuthangle,
        illuminationZenithAngle: s.illuminationzenithangle,
        processingBaseline: s.processingbaseline,
        processingLevel: s.processinglevel,
        onDemand: s.ondemand,
        isDownload: s.isdownload,
        fileName: s.filename,
        link: s.link,
        format: s.format,
        platformName: s.platformname,
        instrumentName: s.instrumentname,
        instrumentShortName: s.instrumentshortname,
        size: s.size,
        productType: s.producttype
      };
      this.datasets.push(newDataset);
    });
  }

  /**
   * Formats satellite dataset dates to improve readability.
   * @param rawDate API response date value
   * @returns formatted date string
   */
  processDate(rawDate: string): string {
    let date = new Date(rawDate);
    let final = date.toLocaleDateString('pt-PT') + ' ' + date.toLocaleTimeString('pt-PT');
    return final;
  }

  /**
   * Updates search terms.
   * Searches datasets by name and source in table component.
   * See {@link TableComponent#filterDataSearchSatellite} for more information. 
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

  // 
  /**
   * Updates the current page of displayed data
   * @param page current page
   */
  getPage(page: any) { this.currentPage = page; }

  /**
   * Opens or closes a single dataset's information display.
   * @param datasetID satellite dataset ID to display or -1 to close
   */
  toggleDatasetView(datasetID: number) {
    // close dataset details
    if (datasetID === -1) {
      this.isDatasetOpen = false;
      this.displayedHeaders = this.headers;

      // reset dropdowns
      this.isDetOpen = false;
      this.isIDsOpen = false;
      this.isDatesOpen = false;
      this.isPercentOpen = false;
      this.isGeoOpen = false;
      this.isProcOpen = false;
      this.isOtherOpen = false;
    }
    // open dataset details
    else {
      this.isDatasetOpen = true;
      this.displayedHeaders = this.openHeaders;

      // find dataset with selected dataset ID
      let datasetIndex = this.datasets.findIndex(item => item.id === datasetID);
      this.openDataset = this.datasets[datasetIndex];
    }
  }

  /**
   * Opens or closes a dataset's details dropdown menu.
   * @param dropID dropdown menu ID to open or close
   * @returns nothing
   */
  toggleInfoDropdown(dropID: string) {
    switch (dropID) {
      case 'details': this.isDetOpen = !this.isDetOpen; return;
      case 'ids': this.isIDsOpen = !this.isIDsOpen; return;
      case 'dates': this.isDatesOpen = !this.isDatesOpen; return;
      case 'percent': this.isPercentOpen = !this.isPercentOpen; return;
      case 'geo': this.isGeoOpen = !this.isGeoOpen; return;
      case 'proc': this.isProcOpen = !this.isProcOpen; return;
      case 'other': this.isOtherOpen = !this.isOtherOpen; return;
    }
  }

  /**
   * Opens Bootstrap modal to delete a satellite dataset.
   * @param content modal content to be displayed
   */
  openDeleteModal(content: any) {
    // reset variables for new modal
    this.isConfChecked = false;
    this.hasClickedRemove = false;

    // open modal
    this.modalService.open(content, { centered: true, size: 'lg' });
  }

  // remove dataset
  /**
   * Checks if the user has confirmed the removal of a satellite dataset.
   * 
   * If there is confirmation, delete a satellite dataset with the API and update the displayed data.
   */
  removeDataset() {
    this.hasClickedRemove = true;
    // without checked confirmation, show error
    if (this.isConfChecked) {
      // remove dataset with API
      this.satServ.deleteSatDataset(this.openDataset.uuid).subscribe(
        (result: any) => {
          // close display
          this.isDatasetOpen = false;
          this.displayedHeaders = this.headers;

          // remove dataset from list
          let datasetIndex = this.datasets.findIndex(item => item.id === this.openDataset.id);
          this.datasets.splice(datasetIndex, 1);

          // update dataset table and pagination
          this.datasets = JSON.parse(JSON.stringify(this.datasets));
          this.updateRowCount(this.datasets.length);
        }, error => { }
      );
      // close
      this.modalService.dismissAll();
    }
  }

}
