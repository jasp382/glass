// Angular Modules
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';

// Leaflet
import { LeafletModule } from '@asymmetrik/ngx-leaflet';
import { LeafletMarkerClusterModule } from "@asymmetrik/ngx-leaflet-markercluster";

// Angular Material
import { MatTabsModule } from '@angular/material/tabs';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatMomentDateModule } from '@angular/material-moment-adapter';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDividerModule } from '@angular/material/divider';
import { MatListModule } from '@angular/material/list';
import { NgxMatDatetimePickerModule, NgxMatTimepickerModule, NgxMatNativeDateModule } from '@angular-material-components/datetime-picker';
import { NgxMatMomentModule } from '@angular-material-components/moment-adapter';

// Style
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

// NGRX Related
import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';

import { appEffects, appReducer } from './stores/app-state';

// Modules
import { AuthModule } from './auth/auth.module';
import { BoffModule } from './boff/boff.module';
import { GeneralModule } from './general/general.module';
import { FeatModule } from './feat/feat.module';
import { GeoportalModule } from './geoportal/geoportal.module';
import { ProfileModule } from './profile/profile.module';

// Lottie
import { LottieModule } from 'ngx-lottie';
import player from 'lottie-web';

// Multi-Language Support
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';

// Components
import { AppComponent } from './app.component';

/**
 * Function to create a player for Lottie aninamtions. Needed for AOT compilation support
 * @returns animation player
 */
export function playerFactory() {
  return player;
}

/**
 * Function to load the translator. Needed for AOT compilation support
 * @param http HTTP client to make the load request
 * @returns new translate loader
 */
export function httpTranslateLoader(http: HttpClient) {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    // Angular
    BrowserModule,
    BrowserAnimationsModule,
    RouterModule,
    FormsModule,
    HttpClientModule,
    AppRoutingModule,

    // Modules
    AuthModule,
    BoffModule,
    GeneralModule,
    FeatModule,
    GeoportalModule,
    ProfileModule,
    
    // Leaflet
    LeafletModule,
    LeafletMarkerClusterModule,

    // Angular Material
    MatTabsModule,
    MatExpansionModule,
    MatSnackBarModule,
    MatTableModule,
    MatDatepickerModule,
    MatToolbarModule,
    MatIconModule,
    MatMomentDateModule,
    MatFormFieldModule,
    MatSidenavModule,
    MatSelectModule,
    MatInputModule,
    MatCheckboxModule,
    MatDividerModule,
    MatListModule,
    NgxMatDatetimePickerModule,
    NgxMatTimepickerModule,
    NgxMatNativeDateModule,
    NgxMatMomentModule,

    FontAwesomeModule,
    NgbModule,

    // Lottie and Language support
    LottieModule.forRoot({ player: playerFactory }),
    TranslateModule.forRoot({
      defaultLanguage: 'pt',
      loader: {
        provide: TranslateLoader,
        useFactory: httpTranslateLoader,
        deps: [HttpClient]
      }
    }),

    // NGRX
    StoreModule.forRoot(appReducer),
    EffectsModule.forRoot(appEffects),
    StoreDevtoolsModule.instrument(),
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
