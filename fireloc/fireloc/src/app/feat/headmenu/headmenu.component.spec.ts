// Modules
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Testing
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';
import { UserService } from 'src/app/serv/rest/users/user.service';

// Components
import { HeadmenuComponent } from './headmenu.component';
import { LoginComponent } from 'src/app/auth/login/login.component';

// Constants
import { routes } from 'src/app/app-routing.module';

// Interfaces
import { Language } from 'src/app/interfaces/language';

// Redux
import { UserActions } from 'src/app/redux/actions/userActions';
import { LangActions } from 'src/app/redux/actions/langActions';
import { selectLanguage, selectUser } from 'src/app/redux/selectors';
import { INITIAL_STATE_USER } from 'src/app/redux/reducers/userReducer';

// Other
import { of, throwError } from 'rxjs';

// Translate
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';

// Mock Auth Service
class MockAuthService {
  isLoggedIn() { }
  logout() { }
}

// Mock User Service
class MockUserService {
  getUser() { }
}

describe('TS29 HeadmenuComponent', () => {
  let component: HeadmenuComponent;
  let fixture: ComponentFixture<HeadmenuComponent>;

  // dependencies
  let modalService: NgbModal;

  // service spies
  let loggedSpy: jasmine.Spy<() => boolean>;

  // mock services
  let authService: AuthService;
  let userService: UserService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        HeadmenuComponent,
      ],
      imports: [
        RouterTestingModule.withRoutes(routes),
        NgbModule,
        NgReduxTestingModule,
        FontAwesomeModule,
        HttpClientTestingModule,
        TranslateModule.forRoot({
          loader: {
            provide: TranslateLoader,
            useFactory: httpTranslateLoader,
            deps: [HttpClient]
          }
        }),
      ],
      providers: [
        { provide: AuthService, useClass: MockAuthService },
        { provide: UserService, useClass: MockUserService },
        NgbModal,
        UserActions,
        LangActions
      ]
    }).compileComponents();

    // reset redux
    MockNgRedux.reset();

    // service
    authService = TestBed.inject(AuthService);
    userService = TestBed.inject(UserService);

    // services spies (default)
    loggedSpy = spyOn(authService, 'isLoggedIn');
    loggedSpy.and.returnValue(false);

    fixture = TestBed.createComponent(HeadmenuComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    // bootstrap modal
    modalService = TestBed.inject(NgbModal);
  });

  afterEach(() => { modalService.dismissAll(); });

  it('T29.1 should create', () => {
    expect(component).toBeTruthy();
  });

  it('T29.2 should check if user is logged in when component is created', () => {
    // initial value
    expect(component.isLoggedIn).toBeFalse();
    expect(loggedSpy).toHaveBeenCalled();
  });

  it('T29.3 should make method calls #onInit', () => {
    // setup spies
    let reduxSubSpy = spyOn(component, 'subscribeToRedux');
    let getUserSpy = spyOn(component, 'getUserInformation');

    // run the onInit Angular Lifecycle Method
    component.ngOnInit();

    // methods should be called
    expect(reduxSubSpy).toHaveBeenCalledOnceWith();
    expect(getUserSpy).toHaveBeenCalledOnceWith();
  });

  it('T29.4 should subscribe to redux to get user information', () => {
    // setup spies
    let reduxSubSpy = spyOn(component, 'subscribeToRedux');
    let getUserSpy = spyOn(component, 'getUserInformation');
    let changeDetSpy = spyOn(component['changeDet'], 'detectChanges');

    // select user state and initialize
    const userStub = MockNgRedux.getSelectorStub(selectUser);
    userStub.next(INITIAL_STATE_USER);
    userStub.complete();

    // run the onInit Angular Lifecycle Method
    component.ngOnInit();

    expect(reduxSubSpy).toHaveBeenCalledOnceWith();
    component.userRedux$.subscribe(
      (actualUserInfo: any) => {
        // user info received should be as expected        
        expect(actualUserInfo).toEqual(INITIAL_STATE_USER);
        expect(getUserSpy).toHaveBeenCalled();
        expect(changeDetSpy).toHaveBeenCalled();
      }
    );
  });

  it('T29.5 should subscribe to redux to get app language', () => {
    // setup spies
    let reduxSubSpy = spyOn(component, 'subscribeToRedux');

    // select language state and initialize
    const langStub = MockNgRedux.getSelectorStub(selectLanguage);
    langStub.next('pt');
    langStub.next('en');
    langStub.complete();

    // run the onInit Angular Lifecycle Method
    component.ngOnInit();

    expect(reduxSubSpy).toHaveBeenCalled();
    component.language$.subscribe(
      (language: any) => {
        // language received should be as expected        
        expect(component.selectedLanguage).toEqual(component.navLanguages[1]);
      }
    );
  });

  it('T29.6 should check user permissions', () => {
    // setup spies
    let checkPermissionSpy = spyOn(component, 'checkPermission').and.callThrough();
    let localStorageGetSpy = spyOn(Storage.prototype, 'getItem').and.returnValue('fireloc');

    let result = component.checkPermission();

    // expectations
    expect(checkPermissionSpy).toHaveBeenCalled();
    expect(localStorageGetSpy).toHaveBeenCalled();
    expect(result).toBeTrue();
  });

  it('T29.7 should not get user information if user is not logged in', () => {
    // setup spies
    let getUserInfoSpy = spyOn(component, 'getUserInformation');
    let getUserSpy = spyOn(userService, 'getUser');

    // initial value
    expect(component.isLoggedIn).toBeFalse();

    // run method
    component.getUserInformation();

    // method should be called
    expect(getUserInfoSpy).toHaveBeenCalledOnceWith();

    // get user should NOT be called
    expect(getUserSpy).not.toHaveBeenCalled();
  });

  it('T29.8 should get user information if user is logged in', () => {
    // expected user info response
    const userInfoRes: any = {
      first_name: 'A',
      last_name: 'F',
      email: 'a@f.com'
    }

    // setup spies
    let getUserInfoSpy = spyOn(component, 'getUserInformation').and.callThrough();
    let getUserSpy = spyOn(userService, 'getUser').and.returnValue(of(userInfoRes));

    // change user logged status
    loggedSpy.and.returnValue(true);

    // initial values
    expect(component.isLoggedIn).toBeFalse();
    expect(component.userName).toBe('');
    expect(component.userEmail).toBe('');

    // run method
    component.getUserInformation();

    // user should be logged in
    expect(component.isLoggedIn).toBeTrue();

    // methods should be called
    expect(getUserInfoSpy).toHaveBeenCalledOnceWith();
    expect(getUserSpy).toHaveBeenCalledOnceWith();

    // user info should be the expected response
    expect(component.userName).toBe(userInfoRes.first_name + ' ' + userInfoRes.last_name);
    expect(component.userEmail).toBe(userInfoRes.email);
  });

  it('T29.9 should not get user information if error with API service', () => {
    // expected user info response
    const userInfoError = throwError(() => new Error());

    // setup spies
    let getUserInfoSpy = spyOn(component, 'getUserInformation').and.callThrough();
    let getUserSpy = spyOn(userService, 'getUser').and.returnValue(userInfoError);

    // change user logged status
    loggedSpy.and.returnValue(true);

    // initial values
    expect(component.isLoggedIn).toBeFalse();
    expect(component.userName).toBe('');
    expect(component.userEmail).toBe('');

    // run method
    component.getUserInformation();

    // user should be logged in
    expect(component.isLoggedIn).toBeTrue();

    // methods should be called
    expect(getUserInfoSpy).toHaveBeenCalledOnceWith();
    expect(getUserSpy).toHaveBeenCalledOnceWith();

    // user info should be unchanged
    expect(component.userName).toBe('');
    expect(component.userEmail).toBe('');
  });

  it('T29.10 should change language with the provided language in #selectLanguage', () => {
    // setup spy
    let selectLangSpy = spyOn(component, 'selectLanguage').and.callThrough();

    // expected value
    let ptLang: Language = component.navLanguages[0];
    let enLang: Language = component.navLanguages[1];

    // initial value
    expect(component.selectedLanguage).toBe(component.navLanguages[0]);

    // call method
    component.selectLanguage(ptLang);
    component.selectLanguage(enLang);

    // expectations should be met
    expect(selectLangSpy).toHaveBeenCalled();
    expect(component.selectedLanguage).toEqual(enLang);

  });

  it('T29.11 should open login modal on #openLogin', () => {
    // setup spies
    let openLoginSpy = spyOn(component, 'openLogin').and.callThrough();
    let loginModalSpy = spyOn(modalService, 'open').and.callThrough();

    component.openLogin();

    // expectations
    expect(openLoginSpy).toHaveBeenCalledOnceWith();
    expect(loginModalSpy).toHaveBeenCalledOnceWith(LoginComponent, { centered: true });
  });

  it('T29.12 should logout user on #logout', () => {
    // user is logged in to log out
    component.isLoggedIn = true;
    fixture.detectChanges();

    // setup spies
    let logoutSpy = spyOn(component, 'logout').and.callThrough();
    let authLogoutSpy = spyOn(authService, 'logout');

    // initial values
    expect(component.isLoggedIn).toBeTrue();

    // method call
    component.logout();

    // expectations
    expect(logoutSpy).toHaveBeenCalledOnceWith();
    expect(authLogoutSpy).toHaveBeenCalledOnceWith();
    expect(component.isLoggedIn).toBeFalse();
  });

});
