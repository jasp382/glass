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
import { MainpComponent } from './mainp/mainp.component';
import { ProfileComponent } from './profile/profile.component';
import { ContribComponent } from './contrib/contrib.component';
import { PasswComponent } from './passw/passw.component';


/**
 * User Profile Module. Contains components related to the User Profile.
 */
@NgModule({
  declarations: [
    MainpComponent,
    ProfileComponent,
    ContribComponent,
    PasswComponent
  ],
  imports: [
    CommonModule,
    FeatModule,
    NgbModule,
    FontAwesomeModule,
    ReactiveFormsModule,
    TranslateModule,
  ]
})
export class ProfileModule { }
