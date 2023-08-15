// Angular Modules
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';

// D3
import 'd3';
import 'nvd3';
import { NvD3Module } from 'ng2-nvd3';

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

// Modules
import { AuthModule } from './auth/auth.module';
import { BoffModule } from './boff/boff.module';
import { FeatModule } from './feat/feat.module';
import { MainiModule } from './maini/maini.module';
import { AppRoutingModule } from './app-routing.module';

// Components
import { AppComponent } from './app.component';
import { NotfoundComponent } from './notfound/notfound.component';
import { HomeComponent } from './home/home.component';

// Services
import { MarkerService } from './serv/leafmap/marker.service';

// Redux
import { DevToolsExtension, NgRedux, NgReduxModule } from '@angular-redux/store';
import { AppState, INITIAL_STATE, rootReducer } from './redux/reducers';
import { AlertActions } from './redux/actions/alertActions';
import { ContributionActions } from './redux/actions/contributionActions';
import { UserActions } from './redux/actions/userActions';
import { DateRangeActions } from './redux/actions/dateRangeActions';
import { EventActions } from './redux/actions/eventActions';
import { RealEventActions } from './redux/actions/realEventActions';
import { LayerActions } from './redux/actions/layerActions';

// Interceptors
import { ErrorInterceptor } from './serv/error-interceptor.interceptor';
import { SuccessInterceptor } from './serv/success.interceptor';

// Lottie
import { LottieModule } from 'ngx-lottie';
import player from 'lottie-web';

// Multi-Language Support
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { LangActions } from './redux/actions/langActions';

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
  return new TranslateHttpLoader(http);
}

@NgModule({
  declarations: [
    AppComponent,
    NotfoundComponent,
    HomeComponent
  ],
  imports: [
    // Angular
    BrowserModule,
    BrowserAnimationsModule,
    RouterModule,
    FormsModule,
    HttpClientModule,

    // Leaflet
    LeafletModule,
    LeafletMarkerClusterModule,

    // Modules
    AppRoutingModule,
    AuthModule,
    BoffModule,
    FeatModule,
    MainiModule,

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
    NvD3Module,
    NgbModule,
    NgReduxModule,

    // Lottie and Language support
    LottieModule.forRoot({ player: playerFactory }),
    TranslateModule.forRoot({
      loader: {
        provide: TranslateLoader,
        useFactory: httpTranslateLoader,
        deps: [HttpClient]
      }
    }),
  ],
  providers: [
    MarkerService,

    // redux actions
    AlertActions,
    ContributionActions,
    UserActions,
    DateRangeActions,
    EventActions,
    RealEventActions,
    LayerActions,
    LangActions,

    // interceptors
    { provide: HTTP_INTERCEPTORS, useClass: SuccessInterceptor, multi: true },
    { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {

  // redux initializer
  constructor(
    public store: NgRedux<AppState>,
    devTools: DevToolsExtension) {
    store.configureStore(
      rootReducer,
      INITIAL_STATE,
      [],
      devTools.isEnabled() ? [devTools.enhancer()] : []
    );
  }
}