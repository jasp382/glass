// Modules
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { FeatModule } from "../../feat/feat.module";

// Components
import { RasterComponent } from './raster/raster.component';
import { SatelliteComponent } from './satellite/satellite.component';
import { VetorialComponent } from './vetorial/vetorial.component';



@NgModule({
  declarations: [
    RasterComponent,
    SatelliteComponent,
    VetorialComponent
  ],
  imports: [
    CommonModule,
    FeatModule,
    FontAwesomeModule,
    NgbModule,
    FormsModule,
    ReactiveFormsModule
  ],
  exports: [
    RasterComponent,
    SatelliteComponent,
    VetorialComponent
  ]
})
export class GeosModule { }
