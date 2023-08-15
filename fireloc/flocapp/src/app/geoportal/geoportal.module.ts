// Angular
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';

// Modules
import { FeatModule } from '../feat/feat.module';

// Bootstrap
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Font Awesome
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

// Components
import { MaincComponent } from './mainc/mainc.component';
import { ChardataComponent } from './chardata/chardata.component';
import { ContribComponent } from './contrib/contrib.component';
import { EventsComponent } from './events/events.component';
import { LayersbarComponent } from './layersbar/layersbar.component';
import { LeftcontrolComponent } from './leftcontrol/leftcontrol.component';
import { LegendComponent } from './legend/legend.component';
import { FirelocsComponent } from './firelocs/firelocs.component';
import { RightcontrolComponent } from './rightcontrol/rightcontrol.component';
import { LayersmapComponent } from './layersmap/layersmap.component';



/**
 * Main Geoportal Module. Contains components related to the Geoportal.
 */
@NgModule({
  declarations: [
    MaincComponent,
    ChardataComponent,
    ContribComponent,
    EventsComponent,
    LayersbarComponent,
    LeftcontrolComponent,
    LegendComponent,
    FirelocsComponent,
    RightcontrolComponent,
    LayersmapComponent
  ],
  imports: [
    CommonModule,
    FeatModule,
    NgbModule,
    FontAwesomeModule,
    FormsModule,
    ReactiveFormsModule,
    TranslateModule,
  ]
})
export class GeoportalModule { }
