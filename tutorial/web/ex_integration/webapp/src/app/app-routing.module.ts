import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { LeafmapComponent } from './leafmap/leafmap.component';
import { LayersComponent } from './layers/layers.component';
import { GeomsComponent } from './geoms/geoms.component';

const routes: Routes = [
  { path: '', redirectTo: 'map', pathMatch: 'full' },
  { path: 'map', component: LeafmapComponent },
  { path: 'layers', component: LayersComponent },
  { path: 'geometries', component: GeomsComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
