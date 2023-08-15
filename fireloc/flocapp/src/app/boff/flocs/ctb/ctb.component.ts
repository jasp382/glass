import { Component, OnInit } from '@angular/core';

// Style
import {
  faChevronDown,
  faGlobeAfrica,
  faUserAlt,
  faCalendarDay,
  faSearch,
  faCamera,
  faMapMarkerAlt,
  faTrash,
  faTimes
} from '@fortawesome/free-solid-svg-icons';
import { NgbDate, NgbModal } from '@ng-bootstrap/ng-bootstrap';

// Constants
import { Extent } from 'src/app/constants/mapext';

// Interfaces
import { TableHeader } from 'src/app/interfaces/backoffice';
import { MapSettings } from 'src/app/interfaces/maps';

/**
 * Backoffice Contributions component.
 * 
 * Displays a list of FireLoc contributions. A single contribution can be viewed or deleted.
 * It is also possible to filter the contributions with search terms, by location, by user or by time period.
 */
@Component({
  selector: 'boff-ctb',
  templateUrl: './ctb.component.html',
  styleUrls: ['./ctb.component.css']
})
export class CtbComponent implements OnInit {

  // icons
  /**
   * icon for dropdown menus
   */
  dropIcon = faChevronDown;
  /**
   * icon for location filter
   */
  locIcon = faGlobeAfrica;
  /**
   * icon for user filter
   */
  userIcon = faUserAlt;
  /**
   * icon for dates
   */
  dateIcon = faCalendarDay;
  /**
   * icon for searches
   */
  searchIcon = faSearch;
  /**
   * icon to display contribution photo
   */
  cameraIcon = faCamera;
  /**
   * icon to display contribution map
   */
  mapIcon = faMapMarkerAlt;
  /**
   * icon for contribution deletion
   */
  deleteIcon = faTrash;
  /**
   * icon to close information
   */
  closeIcon = faTimes;

  /**
   * list of table headers for table component
   */
  headers: TableHeader[] = [
    { objProperty: 'id', columnLabel: '#' },
    { objProperty: 'place', columnLabel: 'Localização' },
    { objProperty: 'date', columnLabel: 'Data' },
    { objProperty: 'fire', columnLabel: 'Fogo Associado' },
    { objProperty: 'dir', columnLabel: 'Direção' },
    { objProperty: 'sunDir', columnLabel: 'Direção do Sol' }
  ];

  /**
   * list of headers to be displayed when a single contribution is closed
   */
  displayedHeaders = this.headers;

  /**
   * search terms for data filtering
   */
  searchTerms: string = '';

  constructor(
    private modalService: NgbModal
  ) { }

  ngOnInit(): void { }

  /**
   * Updates search terms.
   * Searches events by location and fire name in table component. 
   * See {@link TableComponent#filterDataSearchContributions} for more information.
   * @param searchTerms new search terms
   */
  searchContribs(searchTerms: string) {
    // ignore clear search event
    if (typeof (searchTerms) === 'string') this.searchTerms = searchTerms;
  }

}
