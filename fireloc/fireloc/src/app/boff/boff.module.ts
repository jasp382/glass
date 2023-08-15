// Angular
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// Fort Awesome and Bootstrap
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Chart JS
import { ChartsModule } from 'ng2-charts';

// Backoffice Modules
import { UsersModule } from './users/users.module';
import { GeoModule } from './geos/geos.module';
import { ContribModule } from './contrib/contrib.module';
import { MapModule } from './map/map.module';

import { FeatModule } from '../feat/feat.module';

// Backoffice Components
import { MainComponent } from './main/main.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { RealEventsComponent } from './real-events/real-events.component';

/**
 * Backoffice Module. Contains components in the Backoffice.
 */
@NgModule({
  declarations: [MainComponent, DashboardComponent, RealEventsComponent],
  imports: [
    CommonModule,
    RouterModule,
    FontAwesomeModule,
    FeatModule,
    UsersModule,
    GeoModule,
    ContribModule,
    MapModule,
    ChartsModule,
    NgbModule,
    FormsModule,
    ReactiveFormsModule,
  ]
})
export class BoffModule { }
