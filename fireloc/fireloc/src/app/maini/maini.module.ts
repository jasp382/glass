// Angular
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// Modules
import { FeatModule } from '../feat/feat.module';

// Bootstrap
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Font Awesome
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

// Components
import { MainfrontComponent } from './mainfront/mainfront.component';
import { LeftcontrolComponent } from './leftcontrol/leftcontrol.component';
import { RightcontrolComponent } from './rightcontrol/rightcontrol.component';
import { LayersbarComponent } from './layersbar/layersbar.component';
import { LegendComponent } from './legend/legend.component';
import { EventsComponent } from './events/events.component';
import { ContribComponent } from './contrib/contrib.component';
import { ChartdataComponent } from './chartdata/chartdata.component';
import { ProfileComponent } from './profile/profile.component';
import { RealEventsComponent } from './real-events/real-events.component';
import { TranslateModule } from '@ngx-translate/core';

/**
 * Main Geoportal Module. Contains components related to the Geoportal.
 */
@NgModule({
  declarations: [
    MainfrontComponent,
    LeftcontrolComponent,
    RightcontrolComponent,
    LayersbarComponent,
    LegendComponent,
    EventsComponent,
    ContribComponent,
    ChartdataComponent,
    ProfileComponent,
    RealEventsComponent
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
export class MainiModule { }
