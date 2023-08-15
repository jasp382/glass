// Angular
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// Fort Awesome and Bootstrap
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Chart JS
import { NgChartsModule } from 'ng2-charts';

// Modules
import { UsersModule } from './users/users.module';
import { GeosModule } from './geos/geos.module';
import { FlocsModule } from './flocs/flocs.module';
import { MapModule } from './map/map.module';

import { FeatModule } from '../feat/feat.module';

// Backoffice Components
import { MainComponent } from './main/main.component';
import { EventsComponent } from './events/events.component';
import { DashboardComponent } from './dashboard/dashboard.component';



@NgModule({
  declarations: [
    MainComponent,
    EventsComponent,
    DashboardComponent
  ],
  imports: [
    CommonModule,
    RouterModule,
    FontAwesomeModule,
    FeatModule,
    UsersModule,
    GeosModule,
    FlocsModule,
    MapModule,
    NgChartsModule,
    NgbModule,
    FormsModule,
    ReactiveFormsModule,
  ]
})
export class BoffModule { }
