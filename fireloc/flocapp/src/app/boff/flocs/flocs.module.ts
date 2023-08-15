// Modules
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// FireLoc Modules
import { FeatModule } from 'src/app/feat/feat.module';

// Fort Awesome
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

// Bootstrap
import { NgbModule } from "@ng-bootstrap/ng-bootstrap";

// Components
import { FlocsComponent } from './flocs/flocs.component';
import { CtbComponent } from './ctb/ctb.component';



@NgModule({
  declarations: [
    FlocsComponent,
    CtbComponent
  ],
  imports: [
    CommonModule,
    FeatModule,
    FontAwesomeModule,
    NgbModule,
    FormsModule,
    ReactiveFormsModule,
  ],
  exports: [FlocsComponent, CtbComponent]
})
export class FlocsModule { }
