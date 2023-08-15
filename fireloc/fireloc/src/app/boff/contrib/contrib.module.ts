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
import { ContributionsComponent } from './contributions/contributions.component';
import { EventsComponent } from './events/events.component';

/**
 * Backoffice Contributions Module. Contains components in the Backoffice related to FireLoc contributions.
 */
@NgModule({
  declarations: [ContributionsComponent, EventsComponent],
  imports: [
    CommonModule,
    FeatModule,
    FontAwesomeModule,
    NgbModule,
    FormsModule,
    ReactiveFormsModule,
  ],
  exports: [ContributionsComponent, EventsComponent]
})
export class ContribModule { }
