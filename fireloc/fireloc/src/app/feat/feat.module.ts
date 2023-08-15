// Modules
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

// Components
import { HeadmenuComponent } from './headmenu/headmenu.component';
import { LeafmapComponent } from './leafmap/leafmap.component';
import { FormInputComponent } from './form-input/form-input.component';
import { MapFooterComponent } from './map-footer/map-footer.component';
import { SideNavComponent } from './boff/side-nav/side-nav.component';
import { TableComponent } from './boff/table/table.component';
import { SearchComponent } from './boff/search/search.component';
import { PaginationComponent } from './boff/pagination/pagination.component';
import { GraphComponent } from './graph/graph.component';

// Directives
import { HorizontalScrollDirective } from './map-footer/horizontal-scroll.directive';

// Angular Material
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';

// Style
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FlexLayoutModule } from '@angular/flex-layout';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

// Angular Slider
import { NgxSliderModule } from '@angular-slider/ngx-slider';

// Chart JS
import { ChartsModule } from 'ng2-charts';

// Leaflet
import { LeafletMarkerClusterModule } from '@asymmetrik/ngx-leaflet-markercluster';

// Language
import { TranslateModule } from '@ngx-translate/core';

/**
 * Feature Module. Contains components used by other components to prevent code duplication.
 */
@NgModule({
  declarations: [
    HeadmenuComponent,
    LeafmapComponent,
    FormInputComponent,
    MapFooterComponent,
    HorizontalScrollDirective,
    SideNavComponent,
    TableComponent,
    SearchComponent,
    PaginationComponent,
    GraphComponent
  ],
  imports: [
    CommonModule,
    MatTableModule, MatPaginatorModule, MatSortModule, MatSidenavModule, MatListModule, MatToolbarModule, MatIconModule,
    FlexLayoutModule,
    RouterModule,
    NgbModule,
    FontAwesomeModule,
    FormsModule,
    NgxSliderModule,
    ChartsModule,
    LeafletMarkerClusterModule,
    TranslateModule,
  ],
  exports: [
    HeadmenuComponent,
    LeafmapComponent,
    FormInputComponent,
    MapFooterComponent,
    SideNavComponent,
    TableComponent,
    SearchComponent,
    PaginationComponent,
    GraphComponent
  ]
})
export class FeatModule { }
