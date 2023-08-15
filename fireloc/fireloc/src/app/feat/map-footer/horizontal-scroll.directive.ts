import { Directive, ElementRef, EventEmitter, HostListener, Output } from '@angular/core';

/**
 * Horizontal scroll directive.
 * 
 * Detects vertical scroll in the date range element inside the map footer (See {@link MapFooterComponent}) 
 * and transforms it into horizontal scroll.
 */
@Directive({
  selector: '[appHorizontalScroll]'
})
export class HorizontalScrollDirective {

  /**
   * emitter for the scroll value
   */
  @Output() scrollEvent: EventEmitter<number> = new EventEmitter();

  /**
   * Empty constructor
   * @param element unused 
   */
  constructor(private element: ElementRef) { }

  /**
   * Listens to the wheel scroll event and emits the scroll value.
   * @param event scroll event
   */
  @HostListener("wheel", ["$event"])
  public onScroll(event: WheelEvent) {
    this.scrollEvent.emit(event.deltaY);
  }

}
