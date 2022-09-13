import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

import { EcgiComponent } from './ecgi/ecgi.component';
import { GeotmlnhComponent } from './geotmlnh/geotmlnh.component';
import { OsmtolulcComponent } from './osmtolulc/osmtolulc.component';
import { FirelocMobComponent } from './fireloc-mob/fireloc-mob.component';
import { WgeComponent } from './wge/wge.component';

const routes: Routes = [
  // WebGIS Engine URLS
  { path : 'wge', redirectTo: '/wge/map', pathMatch : 'full' },
  { path : 'wge/map', component : WgeComponent }
];

@NgModule({
  declarations: [
    EcgiComponent, GeotmlnhComponent, OsmtolulcComponent,
    FirelocMobComponent, WgeComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ]
})
export class ServModule { }
