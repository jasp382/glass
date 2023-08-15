import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

/**
 * Pagination component.
 * 
 * Used in the Backoffice for table pagination.
 */
@Component({
  selector: 'feat-pagination',
  templateUrl: './pagination.component.html',
  styleUrls: ['./pagination.component.css']
})
export class PaginationComponent implements OnInit {

  /**
   * initial page
   */
  page = 1;

  /**
   * amount of data rows
   */
  @Input('rowCount') rowCount: number = 1;
  /**
   * emitter for the current page
   */
  @Output('page') pageEmitter: EventEmitter<number> = new EventEmitter();

  /**
   * Empty constructor.
   */
  constructor() { }

  /**
   * Empty method.
   */
  ngOnInit(): void { }

  /**
   * Emits the current page for table page change in the Backoffice.
   */
  updatePage() {
    this.pageEmitter.emit(this.page);
  }

}
