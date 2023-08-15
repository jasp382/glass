// Angular
import { Router } from '@angular/router';
import { Location } from "@angular/common";

// Testing
import { ComponentFixture, fakeAsync, flush, TestBed, tick } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';

// Modules
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { MainiModule } from './maini/maini.module';
import { FeatModule } from './feat/feat.module';
import { AuthModule } from './auth/auth.module';
import { BoffModule } from './boff/boff.module';

// Routes
import { routes } from './app-routing.module';

// Components
import { AppComponent } from './app.component';

// Redux
import { AlertActions } from './redux/actions/alertActions';
import { ContributionActions } from './redux/actions/contributionActions';
import { UserActions } from './redux/actions/userActions';
import { DateRangeActions } from './redux/actions/dateRangeActions';
import { EventActions } from './redux/actions/eventActions';
import { LayerActions } from './redux/actions/layerActions';
import { RealEventActions } from './redux/actions/realEventActions';
import { LangActions } from './redux/actions/langActions';
import { selectAlertMessage, selectHasAlert, selectLanguage } from './redux/selectors';
import { INITIAL_STATE_ALERT } from './redux/reducers/alertReducer';

// Guards
import { AuthGuard } from './auth/guards/auth.guard';
import { RoleGuard } from './auth/guards/role.guard';

// Lottie and Language support
import { httpTranslateLoader, playerFactory } from './app.module';
import { LottieModule } from 'ngx-lottie';

describe('TS1 AppComponent', () => {
  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;

  let location: Location;
  let router: Router;
  let routerSpy: any;

  beforeEach(() => {
    // mock guard
    const canActivateStub = () => ({ canActivate: () => true });

    TestBed.configureTestingModule({
      declarations: [AppComponent],
      imports: [
        // Angular
        HttpClientModule,
        // Testing
        RouterTestingModule.withRoutes(routes),
        NgReduxTestingModule,
        // Modules
        MainiModule,
        FeatModule,
        AuthModule,
        BoffModule,
        // Others
        NgbModule,
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
        AlertActions,
        ContributionActions,
        UserActions,
        DateRangeActions,
        EventActions,
        RealEventActions,
        LayerActions,
        LangActions,
        { provide: AuthGuard, useValue: canActivateStub },
        { provide: RoleGuard, useValue: canActivateStub },
      ]
    }).compileComponents();

    // reset redux
    MockNgRedux.reset();

    // component for testing
    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;

    // routing
    router = TestBed.inject(Router);
    location = TestBed.inject(Location);

    // trigger initial data binding
    fixture.detectChanges();

    // setup location change listener and perform initial navigation
    router.initialNavigation();
    routerSpy = spyOn(router, 'navigate').and.callThrough();
  });

  it('T1.1 should create the app', () => { expect(component).toBeTruthy(); });
  it(`T1.2 should have as title 'fireloc'`, () => { expect(component.title).toEqual('fireloc'); });

  // landing page navigation
  it('T1.3 navigate to "" takes to landing page', fakeAsync(() => {
    router.navigate([""]).then(() => {
      expect(location.path()).toBe("/");
      expect(fixture
        .debugElement
        .nativeElement
        .querySelector('app-home')
      ).toBeTruthy();
    });
  }));

  // geoportal navigation
  it('T1.4 navigate to "geoportal" redirects to /geoportal/main/app', fakeAsync(() => {
    router.navigate(["geoportal"]).then(() => {
      expect(location.path()).toBe("/geoportal/main/app");
      expect(fixture
        .debugElement
        .nativeElement
        .querySelector('app-mainfront')
      ).toBeTruthy();
    });
    flush();
  }));

  it('T1.5 navigate to "geoportal/:page" redirects to /geoportal/main/app', fakeAsync(() => {
    router.navigate(["geoportal/:page"]).then(() => {
      expect(location.path()).toBe("/geoportal/main/app");
      expect(fixture
        .debugElement
        .nativeElement
        .querySelector('app-mainfront')
      ).toBeTruthy();
    });
    flush();
  }));

  it('T1.6 navigate to "geoportal/main/app" takes to geoportal', fakeAsync(() => {
    router.navigate(["geoportal/main/app"]).then(() => {
      expect(location.path()).toBe("/geoportal/main/app");
      expect(fixture
        .debugElement
        .nativeElement
        .querySelector('app-mainfront')
      ).toBeTruthy();
    });
    flush();
  }));

  // profile navigation
  it('T1.7 navigate to "profile" takes to profile', fakeAsync(() => {
    router.navigate(["profile"])
      .then(() => {
        expect(routerSpy).toHaveBeenCalledOnceWith(["profile"]);
      })
    flush();
  }));

  it('T1.8 navigate to "profile/password" takes to profile', fakeAsync(() => {
    router.navigate(["profile/password"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["profile/password"]);
    });
    flush();
  }));

  it('T1.9 navigate to "profile/contributions" takes to profile', fakeAsync(() => {
    router.navigate(["profile/contributions"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["profile/contributions"]);
    });
    flush();
  }));

  // backoffice navigation
  it('T1.10 navigate to "admin" redirects to /admin/home', fakeAsync(() => {
    router.navigate(["admin"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin"]);
    });
    flush();
  }));

  it('T1.11 navigate to "admin/home" takes to backoffice dashboard', fakeAsync(() => {
    router.navigate(["admin/home"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/home"]);
    });
    flush();
  }));

  it('T1.12 navigate to "admin/users" takes to backoffice users', fakeAsync(() => {
    router.navigate(["admin/users"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/users"]);
    });
    flush();
  }));

  it('T1.13 navigate to "admin/groups" takes to backoffice groups', fakeAsync(() => {
    router.navigate(["admin/groups"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/groups"]);
    });
    flush();
  }));

  it('T1.14 navigate to "admin/contribs" takes to backoffice contribs', fakeAsync(() => {
    router.navigate(["admin/contribs"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/contribs"]);
    });
    flush();
  }));

  it('T1.15 navigate to "admin/events" takes to backoffice events', fakeAsync(() => {
    router.navigate(["admin/events"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/events"]);
    });
    flush();
  }));

  it('T1.16 navigate to "admin/real-events" takes to backoffice real events', fakeAsync(() => {
    router.navigate(["admin/real-events"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/real-events"]);
    });
    flush();
  }));

  it('T1.17 navigate to "admin/layers" takes to backoffice layers', fakeAsync(() => {
    router.navigate(["admin/layers"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/layers"]);
    });
    flush();
  }));

  it('T1.18 navigate to "admin/legend" takes to backoffice legend', fakeAsync(() => {
    router.navigate(["admin/legend"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/legend"]);
    });
    flush();
  }));

  it('T1.19 navigate to "admin/graphs" takes to backoffice graphs', fakeAsync(() => {
    router.navigate(["admin/graphs"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/graphs"]);
    });
    flush();
  }));

  it('T1.20 navigate to "admin/geo/satellite" takes to backoffice satellite datasets', fakeAsync(() => {
    router.navigate(["admin/geo/satellite"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/geo/satellite"]);
    });
    flush();
  }));

  it('T1.21 navigate to "admin/geo/raster" takes to backoffice raster datasets', fakeAsync(() => {
    router.navigate(["admin/geo/raster"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/geo/raster"]);
    });
    flush();
  }));

  it('T1.22 navigate to "admin/geo/vetorial" takes to backoffice vetorial datasets', fakeAsync(() => {
    router.navigate(["admin/geo/vetorial"]).then(() => {
      expect(routerSpy).toHaveBeenCalledOnceWith(["admin/geo/vetorial"]);
    });
    flush();
  }));

  // other navigation
  it('T1.23 navigate to "unauthorized" takes to unauthorized component', fakeAsync(() => {
    router.navigate(["unauthorized"]).then(() => {
      expect(location.path()).toBe("/unauthorized");
      expect(fixture
        .debugElement
        .nativeElement
        .querySelector('app-unauthorized')
      ).toBeTruthy();
    });
    flush();
  }));

  it('T1.24 navigate to any other url takes to not found component', fakeAsync(() => {
    router.navigate(["profiles"]).then(() => {
      expect(location.path()).toBe("/profiles");
      expect(fixture
        .debugElement
        .nativeElement
        .querySelector('app-notfound')
      ).toBeTruthy();
    });
    flush();
  }));

  it('T1.25 should logout user when browser closes if session is not meant to be kept', () => {
    spyOn(component['authServ'], 'getRememberUser').and.returnValue(false);
    spyOn(component['authServ'], 'isLoggedIn').and.returnValue(true);
    let logoutSpy = spyOn(component['authServ'], 'logout');

    component.ngOnDestroy();

    expect(logoutSpy).toHaveBeenCalled();
  });

  // redux
  it('T1.26 should subscribe to redux for alert messages', () => {
    // spies
    let reduxSubSpy = spyOn(component, 'subscribeToRedux').and.callThrough();
    let showSpy = spyOn(component, 'showAlert');

    // select alert message state and initialize
    const alertStub = MockNgRedux.getSelectorStub(selectAlertMessage);
    alertStub.next(INITIAL_STATE_ALERT.alertMessage);
    alertStub.complete();

    // select has alert state and initialize
    const hasAlertStub = MockNgRedux.getSelectorStub(selectHasAlert);
    hasAlertStub.next(INITIAL_STATE_ALERT.hasAlert);
    hasAlertStub.complete();

    component.subscribeToRedux();

    // expectations
    expect(reduxSubSpy).toHaveBeenCalledOnceWith();
    component.alertMessage$.subscribe(
      (actualInfo: any) => {
        // alert received should be as expected        
        expect(actualInfo).toEqual(INITIAL_STATE_ALERT.alertMessage);
        expect(component.alertMessage).toEqual(INITIAL_STATE_ALERT.alertMessage.message);
        expect(component.alertType).toEqual('warning');
      }
    );
    component.hasAlert$.subscribe(
      (actualInfo: any) => {
        // alert received should be as expected        
        expect(actualInfo).toEqual(INITIAL_STATE_ALERT.hasAlert);
        expect(component.hasAlert).toEqual(INITIAL_STATE_ALERT.hasAlert);
        expect(showSpy).not.toHaveBeenCalledOnceWith();
      }
    );
  });

  it('T1.27 should show alert if received from redux', () => {
    // spies
    let reduxSubSpy = spyOn(component, 'subscribeToRedux').and.callThrough();
    let showSpy = spyOn(component, 'showAlert');

    // select alert message state and initialize
    const alertStub = MockNgRedux.getSelectorStub(selectAlertMessage);
    alertStub.next({ type: 'danger', message: 'Error here' });
    alertStub.complete();

    // select has alert state and initialize
    const hasAlertStub = MockNgRedux.getSelectorStub(selectHasAlert);
    hasAlertStub.next(true);
    hasAlertStub.complete();

    component.subscribeToRedux();

    // expectations
    expect(reduxSubSpy).toHaveBeenCalledOnceWith();
    component.alertMessage$.subscribe(
      (actualInfo: any) => {
        // alert received should be as expected        
        expect(actualInfo).toEqual({ type: 'danger', message: 'Error here' });
        expect(component.alertMessage).toEqual('Error here');
        expect(component.alertType).toEqual('danger');
      }
    );
    component.hasAlert$.subscribe(
      (actualInfo: any) => {
        // alert received should be as expected        
        expect(actualInfo).toEqual(true);
        expect(component.hasAlert).toEqual(true);
        expect(showSpy).toHaveBeenCalled();
      }
    );
  });

  it('T1.28 should close an open alert after 5 seconds', fakeAsync(() => {
    component.hasAlert = true;
    fixture.detectChanges();
    tick();

    let closeSpy = spyOn(component['appAlert'], 'close');
    let actionSpy = spyOn(component['alertActions'], 'resetAlert');
    component.showAlert();
    tick(5000);

    expect(closeSpy).toHaveBeenCalled();
    expect(actionSpy).toHaveBeenCalled();
  }));

  it('T1.29 should update app language from redux', () => {
    // spies
    let reduxSubSpy = spyOn(component, 'subscribeToRedux').and.callThrough();
    let switchSpy = spyOn(component, 'switchLang');

    // select language state and initialize
    const langStub = MockNgRedux.getSelectorStub(selectLanguage);
    langStub.next('pt');
    langStub.complete();

    component.subscribeToRedux();

    // expectations
    expect(reduxSubSpy).toHaveBeenCalledOnceWith();
    component.language$.subscribe(
      (actualInfo: any) => {
        // language received should be as expected        
        expect(actualInfo).toEqual('pt');
        expect(switchSpy).toHaveBeenCalledWith('pt');
      }
    );
  });

  it('T1.30 should update app language', () => {
    // spies
    let switchSpy = spyOn(component, 'switchLang').and.callThrough();
    let translateSpy = spyOn(component['translate'], 'use');

    // select language state and initialize
    const langStub = MockNgRedux.getSelectorStub(selectLanguage);
    langStub.next('pt');
    langStub.complete();

    component.switchLang('pt');

    // expectations
    expect(switchSpy).toHaveBeenCalledWith('pt');
    expect(translateSpy).toHaveBeenCalledWith('pt');
  });

  // language
  it('T1.31 should dispatch action to change language if language is in storage', () => {
    let storageSpy = spyOn(Storage.prototype, 'getItem').and.returnValue('en');
    let changeSpy = spyOn(component['langActions'], 'changeLanguage');
    component.ngOnInit();
    expect(storageSpy).toHaveBeenCalled();
    expect(changeSpy).toHaveBeenCalled();
  });

  it('T1.32 should dispatch not action to change language if language is not storage', () => {
    let storageSpy = spyOn(Storage.prototype, 'getItem').and.returnValue(null);
    let changeSpy = spyOn(component['langActions'], 'changeLanguage');
    component.ngOnInit();
    expect(storageSpy).toHaveBeenCalled();
    expect(changeSpy).not.toHaveBeenCalled();
  });

});
