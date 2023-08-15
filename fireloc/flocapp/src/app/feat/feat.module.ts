// Modules
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

// Directives
//import { HorizontalScrollDirective } from './map-footer/horizontal-scroll.directive';

// Angular Material
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';

// Language
import { TranslateModule } from '@ngx-translate/core';

// Style
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FlexLayoutModule } from '@angular/flex-layout';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

// Angular Slider
import { NgxSliderModule } from '@angular-slider/ngx-slider';

// Leaflet
import { LeafletMarkerClusterModule } from '@asymmetrik/ngx-leaflet-markercluster';

// Components
import { HeadmenuComponent } from './headmenu/headmenu.component';
import { FormInputComponent } from './form-input/form-input.component';
import { LeafmapComponent } from './leafmap/leafmap.component';
import { TableComponent } from './table/table.component';
import { PaginationComponent } from './boff/pagination/pagination.component';
import { SearchComponent } from './boff/search/search.component';
import { SideNavComponent } from './boff/side-nav/side-nav.component';
import { GraphComponent } from './graph/graph.component';
import { MapFooterComponent } from './map-footer/map-footer.component';



@NgModule({
  declarations: [
    HeadmenuComponent,
    FormInputComponent,
    LeafmapComponent,
    TableComponent,
    PaginationComponent,
    SearchComponent,
    SideNavComponent,
    GraphComponent,
    MapFooterComponent
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
    LeafletMarkerClusterModule,
    TranslateModule
  ],
  exports: [
    HeadmenuComponent,
    FormInputComponent,
    LeafmapComponent,
    TableComponent,
    PaginationComponent,
    SearchComponent,
    SideNavComponent,
    GraphComponent,
    MapFooterComponent
  ]
})
export class FeatModule { }
