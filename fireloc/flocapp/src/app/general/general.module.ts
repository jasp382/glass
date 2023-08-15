import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

// Modules
import { FeatModule } from '../feat/feat.module';

// Style
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Language
import { TranslateModule } from '@ngx-translate/core';

// Lottie
import { LottieModule } from 'ngx-lottie';
import player from 'lottie-web';

// Components
import { HomeComponent } from './home/home.component';
import { NotfoundComponent } from './notfound/notfound.component';


/**
 * Function to create a player for Lottie aninamtions. Needed for AOT compilation support
 * @returns animation player
 */
export function playerFactory() {
  return player;
}



@NgModule({
  declarations: [
    HomeComponent,
    NotfoundComponent
  ],
  imports: [
    CommonModule,
    FeatModule,
    
    FontAwesomeModule,
    NgbModule,

    // Lottie and Language support
    LottieModule.forRoot({ player: playerFactory }),

    TranslateModule
  ]
})
export class GeneralModule { }
