import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

// Fort Awesome
import { faSearch } from '@fortawesome/free-solid-svg-icons';

/**
 * Search component.
 * 
 * Displays a search input used in the Backoffice for text search of the table rows.
 */
@Component({
  selector: 'feat-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit {

  /**
   * search input placeholder. if none provided, default value is used.
   */
  @Input('placeholder') placeholder: string = 'Pesquisar...';
  /**
   * search input width. if none provided, default value is used.
   */
  @Input('width') searchWidth: string = '360px';

  /**
   * search terms input from user
   */
  searchTerms: string = '';
  /**
   * emitter for search terms to the parent component
   */
  @Output('search') searchEmitter: EventEmitter<string> = new EventEmitter<string>();

  /**
   * search input icon
   */
  searchIcon = faSearch;

  /**
   * Empty constructor
   */
  constructor() { }

  /**
   * Empty method
   */
  ngOnInit(): void { }

  /**
   * Emits the search terms while the user is typing for better UX.
   * @param terms text input in the search input box
   */
  searchTyping(terms: string) { this.searchTerms = terms; this.searchEmitter.emit(this.searchTerms); }

}
