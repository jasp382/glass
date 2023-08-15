import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';

// Testing
import { NgReduxTestingModule } from '@angular-redux/store/testing';
import { TestBed } from '@angular/core/testing';

// Redux
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';

import { AuthService } from './auth.service';

describe('TS76 AuthService', () => {
  let service: AuthService;

  // dependencies
  let httpClientSpy: jasmine.SpyObj<HttpClient> = jasmine.createSpyObj('HttpClient', ['post', 'put']);
  const routerMock = jasmine.createSpyObj('Router', ['navigate']);

  // local storage
  let localStore: any = {};
  let localStorageGetSpy: jasmine.Spy<(key: string, value: string) => void>;
  let localStorageSetSpy: jasmine.Spy<(key: string, value: string) => void>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        NgReduxTestingModule,
      ],
      providers: [
        AuthService,
        ContributionActions,
        EventActions,
        { provide: Router, useValue: { navigate: routerMock } },
        { provide: HttpClient, useValue: httpClientSpy }
      ]
    });

    // setup
    service = TestBed.inject(AuthService);

    // local storage
    localStorageGetSpy = spyOn(Storage.prototype, 'getItem').and.callFake((key) =>
      key in localStore ? localStore[key] : null
    );
    localStorageSetSpy = spyOn(Storage.prototype, 'setItem').and.callFake(
      (key, value) => (localStore[key] = value + '')
    );
  });

  it('T76.1 should be created', () => { expect(service).toBeTruthy(); });

  it('T76.2 should not set rememberUser value if user is not logged in', () => {
    spyOn(AuthService.prototype, 'isLoggedIn').and.returnValue(false);
    const newService = new AuthService(
      {} as HttpClient,
      {} as Router,
      {} as ContributionActions,
      {} as EventActions
    );

    let setSpy = spyOn(service, 'setRememberUser');
    expect(setSpy).not.toHaveBeenCalled();
  });

  it('T76.3 should send a login POST request', (done) => {
    const expectedResponse = {};

    httpClientSpy.post.and.returnValue(of(expectedResponse));
    service.login('email', 'password').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T76.4 should refresh token data in local storage when API response has data', (done) => {
    const expectedResponse = {
      access_token: 'access_token',
      refresh_token: 'refresh_token',
      expires_in: 'expires_in',
    };
    spyOn(Date, 'now').and.returnValue(10000);

    httpClientSpy.post.and.returnValue(of(expectedResponse));
    service.refreshToken().subscribe(() => {
      expect(localStorageSetSpy).toHaveBeenCalledWith('access_token', 'access_token');
      expect(localStorageSetSpy).toHaveBeenCalledWith('refresh_token', 'refresh_token');
      expect(localStorageSetSpy).toHaveBeenCalledWith('expiration', 'expires_in');
      expect(localStorageSetSpy).toHaveBeenCalledWith('login_time', '10000');
      done();
    });
  });

  it('T76.5 should not refresh token data in local storage when API response does not have specific data', (done) => {
    const expectedResponse = {
      access_token: 'access_token',
      refresh_token: 'refresh_token',
    };

    httpClientSpy.post.and.returnValue(of(expectedResponse));
    service.refreshToken().subscribe((response) => {
      expect(localStorageSetSpy).not.toHaveBeenCalledTimes(4);
      done();
    });
  });

  it('T76.6 should send password recovery PUT request', (done) => {
    const expectedResponse = {};

    httpClientSpy.put.and.returnValue(of(expectedResponse));
    service.resetPassword('email').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T76.7 should send password change PUT request', (done) => {
    const expectedResponse = {};

    httpClientSpy.put.and.returnValue(of(expectedResponse));
    service.changePassword('token', 'password').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T76.8 should send registration POST request for a regular user', (done) => {
    const expectedResponse = {};

    httpClientSpy.post.and.returnValue(of(expectedResponse));
    service.registerUser('name', 'surname', 'email', 'password').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T76.9 should send registration confirmation PUT request', (done) => {
    const expectedResponse = {};

    httpClientSpy.put.and.returnValue(of(expectedResponse));
    service.sendRegistrationConfirmation('email').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  describe('TS76.1 should check if user is logged in', () => {
    it('T76.1.1 should return true if has information in localstorage and token is not expired', () => {
      // setup and spies
      localStore = {
        access_token: 'access_token',
        refresh_token: 'refresh_token',
        type_token: 'type_token',
        expiration: 'expiration',
        userId: 'userId',
        login_time: 'login_time',
        user_role: 'user_role',
      };
      let expiredSpy = spyOn(service, 'isTokenExpired').and.returnValue(false);
      let refreshSpy = spyOn(service, 'refreshToken');

      let result = service.isLoggedIn();

      // expectations
      expect(localStorageGetSpy).toHaveBeenCalledTimes(7);
      expect(expiredSpy).toHaveBeenCalled();
      expect(refreshSpy).not.toHaveBeenCalled();
      expect(result).toBeTrue();
    });
    it('T76.1.2 should return false if token is expired', () => {
      // setup and spies
      localStore = {
        access_token: 'access_token',
        refresh_token: true,
        type_token: 'type_token',
        expiration: 'expiration',
        userId: 'userId',
        login_time: 'login_time',
        user_role: 'user_role',
      };
      let expiredSpy = spyOn(service, 'isTokenExpired').and.returnValue(true);
      let refreshSpy = spyOn(service, 'refreshToken');
      let logoutSpy = spyOn(service, 'logout');

      let result = service.isLoggedIn();

      // expectations
      expect(localStorageGetSpy).toHaveBeenCalledTimes(7);
      expect(expiredSpy).toHaveBeenCalled();
      expect(refreshSpy).toHaveBeenCalled();
      expect(logoutSpy).toHaveBeenCalled();
      expect(result).toBeFalse();
    });
    it('T76.1.3 should return false if it does not have all information in local storage', () => {
      // setup and spies
      localStore = {
        access_token: 'access_token',
        refresh_token: 'refresh_token',
        type_token: 'type_token',
      };
      let expiredSpy = spyOn(service, 'isTokenExpired').and.returnValue(false);
      let refreshSpy = spyOn(service, 'refreshToken');

      let result = service.isLoggedIn();

      // expectations
      expect(localStorageGetSpy).toHaveBeenCalledTimes(7);
      expect(expiredSpy).not.toHaveBeenCalled();
      expect(refreshSpy).not.toHaveBeenCalled();
      expect(result).toBeFalse();
    });
  });

  describe('TS76.2 should check if token is expired', () => {
    it('T76.2.1 should return true if token is expired', () => {
      // setup and spies
      spyOn(Date, 'now').and.returnValue(10000);
      let result = service.isTokenExpired('5', '1');
      // expectations
      expect(result).toBeTrue();
    });
    it('T76.2.2 should return false if token is not expired', () => {
      // setup and spies
      spyOn(Date, 'now').and.returnValue(10000);
      let result = service.isTokenExpired('5', '10000');
      // expectations
      expect(result).toBeFalse();
    });
  });

  it('T76.10 should logout and remove information from storage', () => {
    // setup and spies
    let removeSpy = spyOn(Storage.prototype, 'removeItem');
    let contribAllSpy = spyOn(service['contribActions'], 'removeAllContributions');
    let contribUserSpy = spyOn(service['contribActions'], 'removeUserContributions');
    let eventLayersSpy = spyOn(service['eventActions'], 'clearEventLayers');
    let eventSpy = spyOn(service['eventActions'], 'clearEvents');
    let routerSpy = spyOn(service['router'], 'navigate');

    service.logout();

    // expectations
    expect(removeSpy).toHaveBeenCalledTimes(8);
    expect(contribAllSpy).toHaveBeenCalled();
    expect(contribUserSpy).toHaveBeenCalled();
    expect(eventLayersSpy).toHaveBeenCalled();
    expect(eventSpy).toHaveBeenCalled();
    expect(routerSpy).toHaveBeenCalledWith(['/']);
  });

});
