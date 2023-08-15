// Testing
import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';

// Interfaces and constants
import { Contribution } from 'src/app/interfaces/contribs';
import { routes } from 'src/app/app-routing.module';

// Modules
import { FeatModule } from 'src/app/feat/feat.module';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModal, NgbModalRef, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';

// Redux
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';
import { LangActions } from 'src/app/redux/actions/langActions';
import { UserActions } from 'src/app/redux/actions/userActions';
import { INITIAL_STATE_LANG } from 'src/app/redux/reducers/langReducer';
import { selectLanguage } from 'src/app/redux/selectors';

// Translate
import { httpTranslateLoader } from 'src/app/app.module';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { HttpClient } from '@angular/common/http';

import { ProfileComponent } from './profile.component';

describe('TS41 ProfileComponent', () => {
  let component: ProfileComponent;
  let fixture: ComponentFixture<ProfileComponent>;
  let modalService: NgbModal;
  let mockModalRef: NgbModalRef;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ProfileComponent],
      imports: [
        HttpClientTestingModule,
        FeatModule,
        NgReduxTestingModule,
        RouterTestingModule.withRoutes(routes),
        TranslateModule.forRoot({
          loader: {
            provide: TranslateLoader,
            useFactory: httpTranslateLoader,
            deps: [HttpClient]
          }
        }),
        FormsModule,
        NgbModule,
        ReactiveFormsModule,
        FontAwesomeModule,
      ],
      providers: [
        ContributionActions,
        EventActions,
        UserActions,
        LangActions
      ]
    }).compileComponents();

    // reset redux
    MockNgRedux.reset();

    fixture = TestBed.createComponent(ProfileComponent);
    component = fixture.componentInstance;
    modalService = TestBed.inject(NgbModal);

    fixture.detectChanges();
  });

  it('T41.1 should create', () => { expect(component).toBeTruthy(); });

  it('T41.2 should check if form has password properties in password validator', () => {
    // form to test (coverage purposes only)
    component.passwordForm = new FormGroup({ fakePassword: new FormControl('', []) });
    let validatorSpy = spyOn(component, 'passwordsValidator').and.callThrough();
    fixture.detectChanges();

    //component.onSubmit();
    let validation = component.passwordsValidator(component.passwordForm);
    expect(validatorSpy).toHaveBeenCalled();
    expect(validation).toBeNull();
  });

  it('T41.3 should have password validator returning form error if passwords don\'t match', () => {
    let validatorSpy = spyOn(component, 'passwordsValidator').and.callThrough();
    let result = component.passwordsValidator(new FormGroup({
      password: new FormControl('pass'),
      passwordConfirmation: new FormControl('password')
    }));

    expect(validatorSpy).toHaveBeenCalled();
    expect(result).toEqual({ notSame: true });
  });

  it('T41.4 should subscribe to redux for app language updates', () => {
    // spies
    let reduxSubSpy = spyOn(component, 'subscribeToRedux');

    // select lang state and initialize
    const langStub = MockNgRedux.getSelectorStub(selectLanguage);
    langStub.next(INITIAL_STATE_LANG.language);
    langStub.complete();

    component.subscribeToRedux();

    // expectations
    expect(reduxSubSpy).toHaveBeenCalledOnceWith();
    component.langRedux$.subscribe(
      (actualInfo: any) => {
        // user info received should be as expected        
        expect(actualInfo).toEqual(INITIAL_STATE_LANG.language);
        expect(component.language).toEqual(INITIAL_STATE_LANG.language);
      }
    );
  });

  it('T41.5 should check if user contributions are in local storage', () => {
    let fakeContribs: Contribution = {
      fid: 0, pic: '', location: '', date: { year: 0, month: 0, day: 0 },
      hour: '', minute: '', geom: [], dir: 0, dsun: null
    }
    let storageSpy = spyOn(Storage.prototype, 'getItem');
    
    storageSpy.and.returnValue(JSON.stringify([fakeContribs]));
    component.ngOnInit();
    expect(storageSpy).toHaveBeenCalled();
    expect(component.userContributions).not.toBeNull();

    storageSpy.and.returnValue(null);
    component.ngOnInit();
    expect(storageSpy).toHaveBeenCalled();
  });

  it('T41.6 should activate correct tab with URL check', () => {
    let urlSpy = spyOnProperty(component['router'], 'url', 'get');
    let getSpy = spyOn(component, 'getUserContribs');

    // password
    urlSpy.and.returnValue('something/password');
    component.checkUrl();
    expect(component.activeTab).toBe(3);

    urlSpy.and.returnValue('something/profile');
    component.checkUrl();
    expect(component.activeTab).toBe(2);

    urlSpy.and.returnValue('something/');
    component.checkUrl();
    expect(component.activeTab).toBe(1);
    expect(getSpy).toHaveBeenCalled();
  });

  it('T41.7 should change url on navigate', () => {
    let navigateSpy = spyOn(component['router'], 'navigate');
    component.navigate('password');
    expect(navigateSpy).toHaveBeenCalled();
  });

  describe('TS41.1 User information', () => {
    it('T41.1.1 should get password confirmation value', ()=>{
      expect(component.passwordConfirmationValue?.value).toEqual('');
    });

    it('T41.1.2 should get user information from API', () => {
      let serviceSpy = spyOn(component['userServ'], 'getUser').and.returnValue(of({
        first_name: 'name', last_name: 'surname', email: 'email'
      }));
      component.getUserInfo();
      expect(serviceSpy).toHaveBeenCalled();
      expect(component.userInfo.firstName).toEqual('name');
      expect(component.userInfo.lastName).toEqual('surname');
      expect(component.userInfo.email).toEqual('email');
    });

    it('T41.1.3 should handle error from getting user information from API', () => {
      let serviceSpy = spyOn(component['userServ'], 'getUser').and.returnValue(throwError(() => new Error()));
      component.getUserInfo();
      expect(serviceSpy).toHaveBeenCalled();
      expect(component.userInfo.firstName).toEqual('');
      expect(component.userInfo.lastName).toEqual('');
      expect(component.userInfo.email).toEqual('');
    });

    it('T41.1.4 should update user information with API', () => {
      let serviceSpy = spyOn(component['userServ'], 'updateUser').and.returnValue(of({}));
      let actionSpy = spyOn(component['userActions'], 'getUserInfo');
      component.updateUserInfo();
      expect(serviceSpy).toHaveBeenCalled();
      expect(actionSpy).toHaveBeenCalled();
    });

    it('T41.1.5 should handle error from updating user information with API', () => {
      let serviceSpy = spyOn(component['userServ'], 'updateUser').and.returnValue(throwError(() => new Error()));
      let actionSpy = spyOn(component['userActions'], 'getUserInfo');
      component.updateUserInfo();
      expect(serviceSpy).toHaveBeenCalled();
      expect(actionSpy).not.toHaveBeenCalled();
    });

    it('T41.1.6 should update user password with API', () => {
      let serviceSpy = spyOn(component['userServ'], 'updateUser').and.returnValue(of({}));
      component.changePassword();
      expect(serviceSpy).toHaveBeenCalled();
    });

    it('T41.1.7 should handle error from updating user password with API', () => {
      let serviceSpy = spyOn(component['userServ'], 'updateUser').and.returnValue(throwError(() => new Error()));
      component.changePassword();
      expect(serviceSpy).toHaveBeenCalled();
    });

    it('T41.1.8 should not change user information if profile form is not valid', () => {
      let changeSpy = spyOn(component, 'changeUserInfo').and.callThrough();
      let updateSpy = spyOn(component, 'updateUserInfo');
      component.changeUserInfo();
      expect(changeSpy).toHaveBeenCalled();
      expect(updateSpy).not.toHaveBeenCalled();
    });

    it('T41.1.9 should change user information if profile form is valid', () => {
      let changeSpy = spyOn(component, 'changeUserInfo').and.callThrough();
      let updateSpy = spyOn(component, 'updateUserInfo');
      component.profileForm.patchValue({ firstName: 'name', lastName: 'surname' });
      fixture.detectChanges();

      component.changeUserInfo();
      expect(changeSpy).toHaveBeenCalled();
      expect(updateSpy).toHaveBeenCalled();
    });

    it('T41.1.10 should check if profileForm has the expected form controls', () => {
      // (coverage purposes only)
      let changeSpy = spyOn(component, 'changeUserInfo').and.callThrough();
      spyOn(component, 'updateUserInfo');
      component.profileForm = new FormGroup({ fake: new FormControl('', []) });
      fixture.detectChanges();

      component.changeUserInfo();
      expect(changeSpy).toHaveBeenCalled();
    });

    it('T41.1.11 should not change user password if password form is not valid', () => {
      let changeSpy = spyOn(component, 'changeUserPassword').and.callThrough();
      let updateSpy = spyOn(component, 'changePassword');
      component.changeUserPassword();
      expect(changeSpy).toHaveBeenCalled();
      expect(updateSpy).not.toHaveBeenCalled();
    });

    it('T41.1.12 should change user password if password form is valid', () => {
      let changeSpy = spyOn(component, 'changeUserPassword').and.callThrough();
      let updateSpy = spyOn(component, 'changePassword');
      component.passwordForm.patchValue({ newPassword: 'password', passwordConfirmation: 'password' });
      fixture.detectChanges();

      component.changeUserPassword();
      expect(changeSpy).toHaveBeenCalled();
      expect(updateSpy).toHaveBeenCalled();
    });

    it('T41.1.13 should check if passwordForm has the expected form controls', () => {
      // (coverage purposes only)
      let changeSpy = spyOn(component, 'changeUserPassword').and.callThrough();
      spyOn(component, 'changePassword');
      component.passwordForm = new FormGroup({ fake: new FormControl('', []) });
      fixture.detectChanges();

      component.changeUserPassword();
      expect(changeSpy).toHaveBeenCalled();
    });

    it('T41.1.14 should open delete modal', () => {
      let openSpy = spyOn(component, 'openDeleteModal').and.callThrough();
      let modalSpy = spyOn(component['modalService'], 'open');
      component.openDeleteModal({});
      expect(openSpy).toHaveBeenCalled();
      expect(component.isConfChecked).toBeFalse();
      expect(component.hasClickedRemove).toBeFalse();
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T41.1.15 should not delete user account without confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'deleteAccount').and.callThrough();
      let deleteAPISpy = spyOn(component['userServ'], 'deleteUser');

      component.deleteAccount();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).not.toHaveBeenCalled();
    });

    it('T41.1.16 should delete user account if there was confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'deleteAccount').and.callThrough();
      let deleteAPISpy = spyOn(component['userServ'], 'deleteUser').and.returnValue(of({}));
      let authSpy = spyOn(component['authServ'], 'logout');
      component.isConfChecked = true;
      fixture.detectChanges();

      component.deleteAccount();

      // expectations
      expect(deleteSpy).toHaveBeenCalled();
      expect(deleteAPISpy).toHaveBeenCalled();
      expect(authSpy).toHaveBeenCalled();
    });

    it('T41.1.17 should handle error from deleting user account', () => {
      // spies
      let deleteSpy = spyOn(component, 'deleteAccount').and.callThrough();
      let deleteAPISpy = spyOn(component['userServ'], 'deleteUser').and.returnValue(throwError(() => new Error()));
      let authSpy = spyOn(component['authServ'], 'logout');
      component.isConfChecked = true;
      fixture.detectChanges();

      component.deleteAccount();

      // expectations
      expect(deleteSpy).toHaveBeenCalled();
      expect(deleteAPISpy).toHaveBeenCalled();
      expect(authSpy).not.toHaveBeenCalled();
    });
  });

  describe('TS41.2 User contributions', () => {

    it('T41.2.1 should get user contributions from API (portuguese app language)', () => {
      // setup
      spyOn(Storage.prototype, 'getItem').and.returnValue('email');
      spyOn(Storage.prototype, 'setItem');
      let userContribSpy = spyOn(component, 'getUserContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions').and.returnValue(of({
        data: [{
          fid: 1,
          pic: 'pic',
          fire_name: 'fire',
          datehour: '2022-03-23T19:26:33Z',
          direction: 'dir',
          dsun: 'dsun',
          geom: [{ pid: 1, geom: '(-8.408286 40.195120)' }]
        }]
      }));
      let photoSpy = spyOn(component, 'getContribPhoto').and.returnValue(Promise.resolve(''));
      component.language = 'pt';
      component.userContributions = [];
      fixture.detectChanges();

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalled();
      expect(contribAPISpy).toHaveBeenCalled();
      expect(photoSpy).toHaveBeenCalled();
    });

    it('T41.2.2 should get user contributions from API (english app language)', () => {
      // setup
      spyOn(Storage.prototype, 'getItem').and.returnValue('email');
      spyOn(Storage.prototype, 'setItem');
      let userContribSpy = spyOn(component, 'getUserContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions').and.returnValue(of({
        data: [{
          fid: 1,
          pic: 'pic',
          fire_name: 'fire',
          datehour: '2022-03-23T19:26:33Z',
          direction: 'dir',
          dsun: 'dsun',
          geom: [{ pid: 1, geom: '(-8.408286 40.195120)' }]
        }]
      }));
      let photoSpy = spyOn(component, 'getContribPhoto').and.returnValue(Promise.resolve(''));
      component.language = 'en';
      component.userContributions = [];
      fixture.detectChanges();

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalled();
      expect(contribAPISpy).toHaveBeenCalled();
      expect(photoSpy).toHaveBeenCalled();
    });

    it('T41.2.3 should get user contributions from API and add missing data information (portuguese app language)', () => {
      // setup
      spyOn(Storage.prototype, 'getItem').and.returnValue('email');
      spyOn(Storage.prototype, 'setItem');
      let userContribSpy = spyOn(component, 'getUserContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions').and.returnValue(of({
        data: [{
          fid: 1,
          pic: 'pic',
          datehour: '2022-03-23T19:26:33Z',
          direction: 'dir',
          dsun: 'dsun',
          geom: [{ pid: 1, geom: '(-8.408286 40.195120)' }]
        }]
      }));
      let photoSpy = spyOn(component, 'getContribPhoto').and.returnValue(Promise.resolve(''));
      component.language = 'pt';
      component.userContributions = [];
      fixture.detectChanges();

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalled();
      expect(contribAPISpy).toHaveBeenCalled();
      expect(photoSpy).toHaveBeenCalled();
    });

    it('T41.2.4 should get user contributions from API and add missing data information (english app language)', () => {
      // setup
      spyOn(Storage.prototype, 'getItem').and.returnValue('email');
      spyOn(Storage.prototype, 'setItem');
      let userContribSpy = spyOn(component, 'getUserContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions').and.returnValue(of({
        data: [{
          fid: 1,
          pic: 'pic',
          datehour: '2022-03-23T19:26:33Z',
          direction: 'dir',
          dsun: 'dsun',
          geom: [{ pid: 1, geom: '(-8.408286 40.195120)' }]
        }]
      }));
      let photoSpy = spyOn(component, 'getContribPhoto').and.returnValue(Promise.resolve(''));
      component.language = 'en';
      component.userContributions = [];
      fixture.detectChanges();

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalled();
      expect(contribAPISpy).toHaveBeenCalled();
      expect(photoSpy).toHaveBeenCalled();
    });

    it('T41.2.5 should handle error from user contributions request to API', () => {
      // setup
      let userContribSpy = spyOn(component, 'getUserContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions').and.returnValue(throwError(() => new Error()));
      let photoSpy = spyOn(component, 'getContribPhoto').and.returnValue(Promise.resolve(''));
      component.userContributions = [];
      fixture.detectChanges();

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalled();
      expect(contribAPISpy).toHaveBeenCalled();
      expect(photoSpy).not.toHaveBeenCalled();
    });

    it('T41.2.6 should not get user contributions from API if local storage had them', () => {
      // setup
      let userContribSpy = spyOn(component, 'getUserContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions');
      component.userContributions = [{
        fid: 1, pic: '', location: '', date: { year: 0, month: 0, day: 0 },
        hour: 0, minute: 0, geom: [], dir: 1, dsun: 1
      }];

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).not.toHaveBeenCalled();
    });

    it('T41.2.7 should get contribution photo from API', () => {
      let getPhotoSpy = spyOn(component, 'getContribPhoto').and.callThrough();
      let getPhotoServSpy = spyOn(component['contribServ'], 'getContributionPhoto').and.returnValue(of({ data: 'photoData' }));
      component.getContribPhoto('');
  
      // expectations
      expect(getPhotoSpy).toHaveBeenCalledOnceWith('');
      expect(getPhotoServSpy).toHaveBeenCalledOnceWith('');
    });

    it('T41.2.8 should handle get contribution photo error from API', () => {
      let getPhotoSpy = spyOn(component, 'getContribPhoto').and.callThrough();
      let getPhotoServSpy = spyOn(component['contribServ'], 'getContributionPhoto').and.returnValue(throwError(() => new Error()));
  
      component.getContribPhoto('');
  
      // expectations
      expect(getPhotoSpy).toHaveBeenCalledOnceWith('');
      expect(getPhotoServSpy).toHaveBeenCalledOnceWith('');
    });

    it('T41.2.9 should open user contribution photo', () => {
      let contribution: Contribution = {
        fid: 1, pic: '', location: '', date: { year: 0, month: 0, day: 0 },
        hour: 0, minute: 0, geom: [], dir: 1, dsun: 1
      };
      let openSpy = spyOn(component, 'openContribPhoto').and.callThrough();
      let modalSpy = spyOn(modalService, 'open').and.callThrough();

      component.openContribPhoto(mockModalRef, contribution);

      expect(openSpy).toHaveBeenCalled();
      expect(modalSpy).toHaveBeenCalled();
      modalService.dismissAll();
    });

    it('T41.2.10 should open event information', () => {
      let openSpy = spyOn(component, 'openEvent').and.callThrough();
      component.openEvent();
      expect(openSpy).toHaveBeenCalled();
      expect(component.isEventOpen).toBeTrue();
    });

    it('T41.2.12 should close event information', () => {
      let closeSpy = spyOn(component, 'closeEvent').and.callThrough();
      component.closeEvent();
      expect(closeSpy).toHaveBeenCalled();
      expect(component.isEventOpen).toBeFalse();
    });
  });

});
