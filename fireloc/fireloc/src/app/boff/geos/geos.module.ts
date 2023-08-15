// Modules
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FeatModule } from "../../feat/feat.module";
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// Components
import { RasterComponent } from './raster/raster.component';
import { SatelliteComponent } from './satellite/satellite.component';
import { VetorialComponent } from './vetorial/vetorial.component';

/**
 * Backoffice Geospatial Module. Contains components in the Backoffice with datasets related geospatial information.
 */
@NgModule({
  declarations: [RasterComponent, SatelliteComponent, VetorialComponent],
  exports: [
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
    ReactiveFormsModule,
  ]
})
export class GeoModule { }
