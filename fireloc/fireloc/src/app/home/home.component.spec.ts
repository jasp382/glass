import { of } from 'rxjs';

// Testing
import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';

// Modules
import { FeatModule } from '../feat/feat.module';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Routing
import { RouterTestingModule } from '@angular/router/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { routes } from '../app-routing.module';

// Redux
import { ContributionActions } from '../redux/actions/contributionActions';
import { EventActions } from '../redux/actions/eventActions';
import { UserActions } from '../redux/actions/userActions';
import { LangActions } from '../redux/actions/langActions';

// Components
import { HomeComponent } from './home.component';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from '../app.module';
import { HttpClient } from '@angular/common/http';

// Mock class for NgbModalRef
export class MockNgbModalRef {
  componentInstance = {
    token: '',
  };
  // result: Promise<any> = new Promise((resolve, reject) => resolve(true));
}

describe('TS33 HomeComponent', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;

  // modal
  let modalService: NgbModal;
  let mockModalRef: MockNgbModalRef = new MockNgbModalRef();

  // dependencies
  let router: Router;
  let route: ActivatedRoute;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        HomeComponent,
      ],
      imports: [
        RouterTestingModule.withRoutes(routes),
        HttpClientTestingModule,
        NgReduxTestingModule,
        NgbModule,
        FontAwesomeModule,
        FeatModule,
        TranslateModule.forRoot({
          loader: {
            provide: TranslateLoader,
            useFactory: httpTranslateLoader,
            deps: [HttpClient]
          }
        }),
      ],
      providers: [
        NgbModal,
        ContributionActions,
        EventActions,
        UserActions,
        LangActions,
      ],
    }).compileComponents();

    // reset redux
    //MockNgRedux.reset();

    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    // bootstrap modal
    modalService = TestBed.inject(NgbModal);

    // routing
    router = TestBed.inject(Router);
    route = TestBed.inject(ActivatedRoute);
  });

  afterEach(() => { modalService.dismissAll(); });

  it('T33.1 should create', () => {
    expect(component).toBeTruthy();
  });

  it('T33.2 should get token from url parameter', () => {
    // route
    let routeParams: Map<string, string> = new Map([
      ["reset", ''],
      ["t", '123']
    ]);

    // spies
    spyOnProperty(route, 'queryParamMap').and.returnValue(of(routeParams));
    let openResetSpy = spyOn(component, 'openResetPassword');

    component.ngOnInit();

    expect(openResetSpy).toHaveBeenCalledOnceWith('123');
  });

  it('T33.3 should not get token from url parameter if no token present', () => {
    // route
    let routeParams: Map<string, string> = new Map([]);

    // spies
    spyOnProperty(route, 'queryParamMap').and.returnValue(of(routeParams));
    let openResetSpy = spyOn(component, 'openResetPassword');

    component.ngOnInit();

    expect(openResetSpy).not.toHaveBeenCalled();
  });

  it('T33.4 should prevent url parameter error', () => {
    // route
    let routeParams: Map<string, (string | null)> = new Map([
      ["reset", ''],
      ["t", null]
    ]);

    // spies
    spyOnProperty(route, 'queryParamMap').and.returnValue(of(routeParams));
    let openResetSpy = spyOn(component, 'openResetPassword');

    component.ngOnInit();

    expect(openResetSpy).not.toHaveBeenCalled();
  });

  it('T33.5 should open login modal if user is not logged in', () => {
    // setup spies
    let openLoginSpy = spyOn(component, 'openLogin').and.callThrough();
    let loginModalSpy = spyOn(modalService, 'open').and.returnValue(mockModalRef as any);
    spyOn(component['authServ'], 'isLoggedIn').and.returnValue(false);

    component.openLogin();

    // expectations
    expect(openLoginSpy).toHaveBeenCalledOnceWith();
    expect(loginModalSpy).toHaveBeenCalled();
  });

  it('T33.6 should not open login modal if user is logged in', () => {
    // setup spies
    let openLoginSpy = spyOn(component, 'openLogin').and.callThrough();
    let loginModalSpy = spyOn(modalService, 'open').and.returnValue(mockModalRef as any);
    spyOn(component['authServ'], 'isLoggedIn').and.returnValue(true);

    component.openLogin();

    // expectations
    expect(openLoginSpy).toHaveBeenCalledOnceWith();
    expect(loginModalSpy).not.toHaveBeenCalled();
  });

  it('T33.7 should open register modal if user is not logged in', () => {
    // setup spies
    let openRegisterSpy = spyOn(component, 'openRegister').and.callThrough();
    let registerModalSpy = spyOn(modalService, 'open').and.returnValue(mockModalRef as any);
    spyOn(component['authServ'], 'isLoggedIn').and.returnValue(false);

    component.openRegister();

    // expectations
    expect(openRegisterSpy).toHaveBeenCalledOnceWith();
    expect(registerModalSpy).toHaveBeenCalled();
  });

  it('T33.8 should not open register modal if user is logged in', () => {
    // setup spies
    let openRegisterSpy = spyOn(component, 'openRegister').and.callThrough();
    let registerModalSpy = spyOn(modalService, 'open').and.returnValue(mockModalRef as any);
    spyOn(component['authServ'], 'isLoggedIn').and.returnValue(true);

    component.openRegister();

    // expectations
    expect(openRegisterSpy).toHaveBeenCalledOnceWith();
    expect(registerModalSpy).not.toHaveBeenCalled();
  });

  it('T33.9 should open reset passowrd modal if user is not logged in', () => {
    // setup spies
    let openResetSpy = spyOn(component, 'openResetPassword').and.callThrough();
    let resetModalSpy = spyOn(modalService, 'open').and.returnValue(mockModalRef as any);
    spyOn(component['authServ'], 'isLoggedIn').and.returnValue(false);

    component.openResetPassword('1234');

    // expectations
    expect(openResetSpy).toHaveBeenCalledOnceWith('1234');
    expect(resetModalSpy).toHaveBeenCalled();
    expect(mockModalRef.componentInstance.token).toEqual('1234');
  });

  it('T33.10 should not open reset passowrd modal if user is logged in', () => {
    // setup spies
    let openResetSpy = spyOn(component, 'openResetPassword').and.callThrough();
    let resetModalSpy = spyOn(modalService, 'open').and.returnValue(mockModalRef as any);
    spyOn(component['authServ'], 'isLoggedIn').and.returnValue(true);

    component.openResetPassword('1234');

    // expectations
    expect(openResetSpy).toHaveBeenCalledOnceWith('1234');
    expect(resetModalSpy).not.toHaveBeenCalled();
  });

});
