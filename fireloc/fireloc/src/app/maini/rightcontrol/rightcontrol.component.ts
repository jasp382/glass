import { Component, EventEmitter, OnInit, Output } from '@angular/core';

/**
 * Geoportal Right menu component.
 * 
 * Displays the right menu in the Geoportal. 
 * Hosts the content for Geoportal FireLoc Events, Geoportal Contributions, Geoportal Real Events, and Geoportal Graphs components.
 */
@Component({
  selector: 'app-rightcontrol',
  templateUrl: './rightcontrol.component.html',
  styleUrls: ['./rightcontrol.component.css']
})
export class RightcontrolComponent implements OnInit {

  /**
   * emitter for the active tab in the right menu
   */
  @Output('activeTab') activeEmitter = new EventEmitter<number>();
  /**
   * emitter for the flag that determines is all contributions are selected
   */
  @Output('allContribsSelected') allContribsEmitter = new EventEmitter<boolean>();

  /**
   * information if all contributions are shown (true, false for user, undefined for nothing)
   */
  allContribsSelected: boolean | undefined;

  /**
   * current active right menu tab
   */
  activeTab: number = 0;
  /**
   * flag to determine if first tab is active (FireLoc events)
   */
  tab1Active = false;
  /**
   * flag to determine if second tab is active (contributions)
   */
  tab2Active = false;
  /**
   * flag to determine if third tab is active (real events)
   */
  tab3Active = false;
  /**
   * flag to determine if fourth tab is active (graphs)
   */
  tab4Active = false;

  /**
   * Empty constructor
   */
  constructor() { }

  /**
   * Empty method
   */
  ngOnInit(): void { }

  /**
   * Opens and closes menu tabs. Allows tab to close when clicked if already opened.
   * Emits the active tab to parent component.
   * @param tabNumber selected tab number
   */
  toggleTab(tabNumber: number) {
    switch (tabNumber) {
      // fireloc events
      case 1:
        // toggle tab
        if (this.tab1Active) { this.tab1Active = false; this.activeTab = 0; }
        else this.tab1Active = true;

        // reset other tabs
        this.tab2Active = false;
        this.tab3Active = false;
        this.tab4Active = false;
        break;
      // contributions
      case 2:
        // toggle tab
        if (this.tab2Active) { this.tab2Active = false; this.activeTab = 0; }
        else this.tab2Active = true;

        // reset other tabs
        this.tab1Active = false;
        this.tab3Active = false;
        this.tab4Active = false;
        break;
      // real events
      case 3:
        // toggle tab
        if (this.tab3Active) { this.tab3Active = false; this.activeTab = 0; }
        else this.tab3Active = true;

        // reset other tabs
        this.tab1Active = false;
        this.tab2Active = false;
        this.tab4Active = false;
        break;
      // graphs
      case 4:
        // toggle tab
        if (this.tab4Active) { this.tab4Active = false; this.activeTab = 0; }
        else this.tab4Active = true;

        // reset other tabs
        this.tab1Active = false;
        this.tab2Active = false;
        this.tab3Active = false;
        break;
    }
    this.activeEmitter.emit(this.activeTab);
  }

  /**
   * Receives the flag that determines if all FireLoc contributions are displayed.
   * Emits the value to parent component.
   * @param event flag value (true or false)
   */
  receiveContribToggle(event: boolean) {
    this.allContribsSelected = event;
    this.allContribsEmitter.emit(event);
  }

}
