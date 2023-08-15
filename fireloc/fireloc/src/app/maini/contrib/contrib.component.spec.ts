// Testing
import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';

// Modules
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FeatModule } from 'src/app/feat/feat.module';

// Redux
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';
import { UserActions } from 'src/app/redux/actions/userActions';
import { selectAllContribs, selectDateRange, selectLanguage, selectUser, selectUserContribs } from 'src/app/redux/selectors';
import { INITIAL_STATE_CONTRIB } from 'src/app/redux/reducers/contributionReducer';
import { INITIAL_STATE_DATERANGE } from 'src/app/redux/reducers/dateRangeReducer';
import { INITIAL_STATE_USER } from 'src/app/redux/reducers/userReducer';
import { INITIAL_STATE_LANG } from 'src/app/redux/reducers/langReducer';

// Interfaces & Constants
import { ContribDate, Contribution, ContributionDateGroup } from 'src/app/interfaces/contribs';
import { routes } from 'src/app/app-routing.module';

// Component
import { ContribComponent } from './contrib.component';

// Other
import { of, Subscription, throwError } from 'rxjs';
import { By } from '@angular/platform-browser';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';

describe('TS35 ContribComponent', () => {
  let component: ContribComponent;
  let fixture: ComponentFixture<ContribComponent>;

  let modalService: NgbModal;
  let modal: NgbActiveModal;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        ContribComponent,
      ],
      imports: [
        HttpClientTestingModule,
        FontAwesomeModule,
        FormsModule,
        ReactiveFormsModule,
        RouterTestingModule.withRoutes(routes),
        NgReduxTestingModule,
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
        NgbActiveModal,
        ContributionActions,
        EventActions,
        UserActions,
      ]
    }).compileComponents();

    // reset redux
    MockNgRedux.reset();

    fixture = TestBed.createComponent(ContribComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    // bootstrap modal
    modal = TestBed.inject(NgbActiveModal);
    modalService = TestBed.inject(NgbModal);
  });

  afterEach(() => { modal.close(); modalService.dismissAll(); fixture.destroy(); });

  it('T35.1 should create', () => { expect(component).toBeTruthy(); });

  describe('TS35.1 Redux subscriptions', () => {
    it('T35.1.1 should subscribe to redux for all contributions', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');

      // select all contribs state and initialize
      const contribStub = MockNgRedux.getSelectorStub(selectAllContribs);
      contribStub.next(INITIAL_STATE_CONTRIB.allContributions);
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.allContributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_CONTRIB.allContributions);
          expect(component.allContributionsDateGroups).toEqual(INITIAL_STATE_CONTRIB.allContributions);
          expect(component.fullContributionsDateGroups).toEqual(INITIAL_STATE_CONTRIB.allContributions);
          expect(component.noContribs).toBeTrue();
        }
      );
    });

    it('T35.1.2 should display all contributions from redux subscription', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      spyOn(Storage.prototype, 'getItem').and.returnValue('fireloc');

      // select all contribs state and add fake data
      let fakeContribGroup = [{ date: { year: 2022, month: 11, day: 14 }, contributions: [] }];
      const contribStub = MockNgRedux.getSelectorStub(selectAllContribs);
      contribStub.next(fakeContribGroup);
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.allContributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(fakeContribGroup);
          expect(component.allContributionsDateGroups).toEqual(fakeContribGroup);
          expect(component.fullContributionsDateGroups).toEqual(fakeContribGroup);
          expect(component.noContribs).toBeFalse();
          expect(component.loadingContribs).toBeFalse();
        }
      );
    });

    it('T35.1.3 should not display all contributions from redux subscription if user does not have permission', () => {
      // spies and setup
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      spyOn(Storage.prototype, 'getItem').and.returnValue('justauser');

      component.ngOnInit();

      // select all contribs state and add fake data
      let fakeContribGroup = [{ date: { year: 2022, month: 11, day: 14 }, contributions: [] }];
      const contribStub = MockNgRedux.getSelectorStub(selectAllContribs);
      contribStub.next(fakeContribGroup);
      contribStub.complete();

      // expectations
      expect(component.hasPermission).toBeFalse();
      expect(component.allContribSelected).toBeFalse();
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.allContributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(fakeContribGroup);
          expect(component.allContribSelected).toBeFalse();
          expect(component.hasPermission).toBeFalse();
          expect(component.allContributionsDateGroups).toEqual(fakeContribGroup);
          expect(component.fullContributionsDateGroups).toEqual([]);
          expect(component.noContribs).toBeFalse();
        }
      );
    });

    it('T35.1.4 should subscribe to redux for user contributions', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');

      // select all contribs state and initialize
      const contribStub = MockNgRedux.getSelectorStub(selectUserContribs);
      contribStub.next(INITIAL_STATE_CONTRIB.userContributions);
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.userContributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_CONTRIB.userContributions);
          expect(component.allContributionsDateGroups).toEqual(INITIAL_STATE_CONTRIB.userContributions);
          expect(component.fullContributionsDateGroups).toEqual(INITIAL_STATE_CONTRIB.userContributions);
          expect(component.noContribs).toBeTrue();
        }
      );
    });

    it('T35.1.5 should display user contributions from redux subscription', () => {
      // spies and setup
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      component.allContribSelected = false;
      fixture.detectChanges();

      // select all contribs state and add fake data
      let fakeContribGroup = [{ date: { year: 2022, month: 11, day: 14 }, contributions: [] }];
      const contribStub = MockNgRedux.getSelectorStub(selectUserContribs);
      contribStub.next(fakeContribGroup);
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.userContributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(fakeContribGroup);
          expect(component.fullContributionsDateGroups).toEqual(fakeContribGroup);
          expect(component.noContribs).toBeFalse();
          expect(component.loadingContribs).toBeFalse();
        }
      );
    });

    it('T35.1.6 should keep loading state if no user contributions from redux subscription', () => {
      // spies and setup
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      component.allContribSelected = false;
      fixture.detectChanges();

      // select all contribs state and add fake data
      const contribStub = MockNgRedux.getSelectorStub(selectUserContribs);
      contribStub.next(INITIAL_STATE_CONTRIB.userContributions);
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.userContributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_CONTRIB.userContributions);
          expect(component.fullContributionsDateGroups).toEqual(INITIAL_STATE_CONTRIB.userContributions);
          expect(component.noContribs).toBeTrue();
          expect(component.loadingContribs).toBeTrue();
        }
      );
    });

    it('T35.1.7 should subscribe to redux for date range', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let filterContribSpy = spyOn(component, 'filterContributionsByDate');

      // select date range state and initialize
      const rangeStub = MockNgRedux.getSelectorStub(selectDateRange);
      rangeStub.next(INITIAL_STATE_DATERANGE);
      rangeStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.dateRange$.subscribe(
        (actualInfo: any) => {
          // info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_DATERANGE);
          expect(component.minDate).toEqual(INITIAL_STATE_DATERANGE.minDate);
          expect(component.maxDate).toEqual(INITIAL_STATE_DATERANGE.maxDate);
          expect(filterContribSpy).toHaveBeenCalled();
        }
      );
    });

    it('T35.1.8 should display contributions after date range update in redux', () => {
      // spies and setup
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let filterContribSpy = spyOn(component, 'filterContributionsByDate');
      let fakeContribGroup = [{ date: { year: 2022, month: 11, day: 14 }, contributions: [] }];
      component.fullContributionsDateGroups = fakeContribGroup;
      fixture.detectChanges();

      // select all contribs state and initialize
      const rangeStub = MockNgRedux.getSelectorStub(selectDateRange);
      rangeStub.next(INITIAL_STATE_DATERANGE);
      rangeStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.dateRange$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_DATERANGE);
          expect(component.minDate).toEqual(INITIAL_STATE_DATERANGE.minDate);
          expect(component.maxDate).toEqual(INITIAL_STATE_DATERANGE.maxDate);
          expect(filterContribSpy).toHaveBeenCalled();
          expect(component.noContribs).toBeFalse();
          expect(component.loadingContribs).toBeFalse();
        }
      );
    });

    it('T35.1.9 should subscribe to redux for user information updates (logged in, with permissions)', () => {
      // spies
      spyOn(Storage.prototype, 'getItem').and.returnValue('fireloc');
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let authSpy = spyOn(component['authServ'], 'isLoggedIn').and.returnValue(true);
      let allSpy = spyOn(component, 'getAllContribs');
      let userSpy = spyOn(component, 'getUserContribs');
      let emitterSpy = spyOn(component['toggleEmitter'], 'emit');
      let eventsSpy = spyOn(component, 'getEventsToken');

      // select user state and initialize
      const userStub = MockNgRedux.getSelectorStub(selectUser);
      userStub.next(INITIAL_STATE_USER);
      userStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.userRedux$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_USER);
          expect(authSpy).toHaveBeenCalled();
          expect(component.isLoggedIn).toBeTrue();
          expect(component.hasPermission).toBeTrue();
          expect(allSpy).toHaveBeenCalled();
          expect(userSpy).toHaveBeenCalled();
          expect(emitterSpy).toHaveBeenCalled();
          expect(eventsSpy).toHaveBeenCalled();
        }
      );
    });

    it('T35.1.10 should subscribe to redux for user information updates (logged in, without permissions)', () => {
      // spies
      spyOn(Storage.prototype, 'getItem').and.returnValue('justauser');
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let authSpy = spyOn(component['authServ'], 'isLoggedIn').and.returnValue(true);
      let allSpy = spyOn(component, 'getAllContribs');
      let userSpy = spyOn(component, 'getUserContribs');
      let emitterSpy = spyOn(component['toggleEmitter'], 'emit');
      let eventsSpy = spyOn(component, 'getEventsToken');

      // select user state and initialize
      const userStub = MockNgRedux.getSelectorStub(selectUser);
      userStub.next(INITIAL_STATE_USER);
      userStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.userRedux$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_USER);
          expect(authSpy).toHaveBeenCalled();
          expect(component.isLoggedIn).toBeTrue();
          expect(component.hasPermission).toBeFalse();
          expect(allSpy).not.toHaveBeenCalled();
          expect(component.allContribSelected).toBeFalse();
          expect(userSpy).toHaveBeenCalled();
          expect(emitterSpy).toHaveBeenCalled();
          expect(eventsSpy).toHaveBeenCalled();
        }
      );
    });

    it('T35.1.11 should subscribe to redux for user information updates (not logged in)', () => {
      // spies
      spyOn(Storage.prototype, 'getItem').and.returnValue('justauser');
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let authSpy = spyOn(component['authServ'], 'isLoggedIn').and.returnValue(false);
      let allSpy = spyOn(component, 'getAllContribs');
      let userSpy = spyOn(component, 'getUserContribs');
      let emitterSpy = spyOn(component['toggleEmitter'], 'emit');
      let eventsSpy = spyOn(component, 'getEventsToken');

      // select user state and initialize
      const userStub = MockNgRedux.getSelectorStub(selectUser);
      userStub.next(INITIAL_STATE_USER);
      userStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.userRedux$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_USER);
          expect(authSpy).toHaveBeenCalled();
          expect(component.isLoggedIn).toBeFalse();
          expect(component.hasPermission).toBeFalse();
          expect(allSpy).not.toHaveBeenCalled();
          expect(userSpy).not.toHaveBeenCalled();
          expect(emitterSpy).not.toHaveBeenCalled();
          expect(eventsSpy).not.toHaveBeenCalled();
        }
      );
    });

    it('T35.1.12 should subscribe to redux for app language updates', () => {
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

    it('T35.1.13 should unsubscribe from redux selectors when component is destroyed', () => {
      // spies
      let allSpy = spyOn(component.allContribSub, 'unsubscribe');
      let userSpy = spyOn(component.userContribSub, 'unsubscribe');
      let dateSpy = spyOn(component.dateRangeSub, 'unsubscribe');
      let userInfoSpy = spyOn(component.userSub, 'unsubscribe');
      let langSpy = spyOn(component.langSub, 'unsubscribe');

      component.ngOnDestroy();

      // expectations
      expect(allSpy).toHaveBeenCalled();
      expect(userSpy).toHaveBeenCalled();
      expect(dateSpy).toHaveBeenCalled();
      expect(userInfoSpy).toHaveBeenCalled();
      expect(langSpy).toHaveBeenCalled();
    });

    it('T35.1.14 should not unsubscribe from redux selectors if subscriptions were not created', () => {
      // spies and setup
      let allSpy = spyOn(component.allContribSub, 'unsubscribe');
      let userSpy = spyOn(component.userContribSub, 'unsubscribe');
      let dateSpy = spyOn(component.dateRangeSub, 'unsubscribe');
      let userInfoSpy = spyOn(component.userSub, 'unsubscribe');
      let langSpy = spyOn(component.langSub, 'unsubscribe');

      let sub!: Subscription;
      component.allContribSub = sub;
      component.userContribSub = sub;
      component.dateRangeSub = sub;
      component.userSub = sub;
      component.langSub = sub;
      fixture.detectChanges();

      component.ngOnDestroy();

      // expectations
      expect(allSpy).not.toHaveBeenCalled();
      expect(userSpy).not.toHaveBeenCalled();
      expect(dateSpy).not.toHaveBeenCalled();
      expect(userInfoSpy).not.toHaveBeenCalled();
      expect(langSpy).not.toHaveBeenCalled();
    });
  });

  describe('TS35.2 Get contributions', () => {
    it('T35.2.1 should get all contributions if user has permissions', () => {
      // spies
      let allContribsSpy = spyOn(component, 'getAllContribs');
      let userContribsSpy = spyOn(component, 'getUserContribs');
      spyOn(Storage.prototype, 'getItem').and.returnValue('fireloc');

      component.ngOnInit();

      // expectations
      expect(component.isLoggedIn).toBeTrue();
      expect(component.hasPermission).toBeTrue();
      expect(allContribsSpy).toHaveBeenCalled();
      expect(userContribsSpy).toHaveBeenCalled();
    });

    it('T35.2.2 should get user contributions if user is logged in but does not have permissions', () => {
      // spies
      let userContribsSpy = spyOn(component, 'getUserContribs');
      spyOn(Storage.prototype, 'getItem').and.returnValue('justauser');

      component.ngOnInit();

      // expectations
      expect(component.isLoggedIn).toBeTrue();
      expect(component.hasPermission).toBeFalse();
      expect(component.allContribSelected).toBeFalse();
      expect(userContribsSpy).toHaveBeenCalled();
    });

    it('T35.2.3 should not get contributions if user is not logged in', () => {
      // spies
      let allContribsSpy = spyOn(component, 'getAllContribs');
      let userContribsSpy = spyOn(component, 'getUserContribs');
      component.isLoggedIn = false;
      fixture.detectChanges();

      component.ngOnInit();

      expect(component.isLoggedIn).toBeFalse();
      expect(component.hasPermission).toBeFalse();
      expect(allContribsSpy).not.toHaveBeenCalled();
      expect(userContribsSpy).not.toHaveBeenCalled();
    });

    it('T35.2.4 should get all contributions from API (portuguese app language)', () => {
      // setup
      let allContribSpy = spyOn(component, 'getAllContribs').and.callThrough();
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
      let groupSpy = spyOn(component, 'groupContribByDate');

      component.getAllContribs();

      // expectations
      expect(allContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).toHaveBeenCalledOnceWith();
      expect(groupSpy).toHaveBeenCalledOnceWith(component.allContributions, 'all');
    });

    it('T35.2.5 should get all contributions from API (english app language)', () => {
      // setup
      let allContribSpy = spyOn(component, 'getAllContribs').and.callThrough();
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
      let groupSpy = spyOn(component, 'groupContribByDate');
      component.language = 'en';
      fixture.detectChanges();

      component.getAllContribs();

      // expectations
      expect(allContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).toHaveBeenCalledOnceWith();
      expect(groupSpy).toHaveBeenCalledOnceWith(component.allContributions, 'all');
    });

    it('T35.2.6 should get all contributions from API and add missing data information (portuguese app language)', () => {
      // setup
      let allContribSpy = spyOn(component, 'getAllContribs').and.callThrough();
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
      let groupSpy = spyOn(component, 'groupContribByDate');

      component.getAllContribs();

      // expectations
      expect(allContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).toHaveBeenCalledOnceWith();
      expect(groupSpy).toHaveBeenCalledOnceWith(component.allContributions, 'all');
    });

    it('T35.2.7 should get all contributions from API and add missing data information (english app language)', () => {
      // setup
      let allContribSpy = spyOn(component, 'getAllContribs').and.callThrough();
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
      let groupSpy = spyOn(component, 'groupContribByDate');
      component.language = 'en';
      fixture.detectChanges();

      component.getAllContribs();

      // expectations
      expect(allContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).toHaveBeenCalledOnceWith();
      expect(groupSpy).toHaveBeenCalledOnceWith(component.allContributions, 'all');
    });

    it('T35.2.8 should handle error from all contributions request to API', () => {
      // setup
      let allContribSpy = spyOn(component, 'getAllContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions')
        .and.returnValue(throwError(() => new Error()));
      let groupSpy = spyOn(component, 'groupContribByDate');

      component.getAllContribs();

      // expectations
      expect(allContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).toHaveBeenCalledOnceWith();
      expect(groupSpy).not.toHaveBeenCalled();
    });

    it('T35.2.9 should not get all contributions from API if redux had them', () => {
      // setup
      let allContribSpy = spyOn(component, 'getAllContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions');
      component.allContributionsDateGroups = [{
        date: { year: 2022, month: 11, day: 15 },
        contributions: []
      }];

      component.getAllContribs();

      // expectations
      expect(allContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).not.toHaveBeenCalled();
    });

    it('T35.2.10 should get user contributions from API (portuguese app language)', () => {
      // setup
      spyOn(Storage.prototype, 'getItem').and.returnValue('email');
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
      let groupSpy = spyOn(component, 'groupContribByDate');

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).toHaveBeenCalledOnceWith('email');
      expect(groupSpy).toHaveBeenCalledOnceWith(component.userContributions, 'user');
    });

    it('T35.2.11 should get user contributions from API (english app language)', () => {
      // setup
      spyOn(Storage.prototype, 'getItem').and.callFake((key) => 'email');
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
      let groupSpy = spyOn(component, 'groupContribByDate');
      component.language = 'en';
      fixture.detectChanges();

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).toHaveBeenCalledOnceWith('email');
      expect(groupSpy).toHaveBeenCalledOnceWith(component.userContributions, 'user');
    });

    it('T35.2.12 should get user contributions from API and add missing data information (portuguese app language)', () => {
      // setup
      spyOn(Storage.prototype, 'getItem').and.returnValue('email');
      let userContribSpy = spyOn(component, 'getUserContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions')
        .and.returnValue(of({
          data: [{
            fid: 1,
            pic: 'pic',
            datehour: '2022-03-23T19:26:33Z',
            direction: 'dir',
            dsun: 'dsun',
            geom: [{ pid: 1, geom: '(-8.408286 40.195120)' }]
          }]
        }));
      let groupSpy = spyOn(component, 'groupContribByDate');

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).toHaveBeenCalledOnceWith('email');
      expect(groupSpy).toHaveBeenCalledOnceWith(component.userContributions, 'user');
    });

    it('T35.2.13 should get user contributions from API and add missing data information (english app language)', () => {
      // setup
      spyOn(Storage.prototype, 'getItem').and.returnValue('email');
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
      let groupSpy = spyOn(component, 'groupContribByDate');
      component.language = 'en';
      fixture.detectChanges();

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).toHaveBeenCalledOnceWith('email');
      expect(groupSpy).toHaveBeenCalledOnceWith(component.userContributions, 'user');
    });

    it('T35.2.14 should handle error from user contributions request to API', () => {
      // setup
      let userContribSpy = spyOn(component, 'getUserContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions')
        .and.returnValue(throwError(() => new Error()));
      let groupSpy = spyOn(component, 'groupContribByDate');

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).toHaveBeenCalledOnceWith('email');
      expect(groupSpy).not.toHaveBeenCalled();
    });

    it('T35.2.15 should not get user contributions from API if redux had them', () => {
      // setup
      let userContribSpy = spyOn(component, 'getUserContribs').and.callThrough();
      let contribAPISpy = spyOn(component['contribServ'], 'getContributions');
      component.userContributionsDateGroups = [{
        date: { year: 2022, month: 11, day: 15 },
        contributions: []
      }];

      component.getUserContribs();

      // expectations
      expect(userContribSpy).toHaveBeenCalledOnceWith();
      expect(contribAPISpy).not.toHaveBeenCalled();
    });
  });

  describe('TS35.3 Filter contributions by date', () => {
    // date filter
    it('T35.3.1 should filter contributions with date range (portuguese app language)', () => {
      let filterSpy = spyOn(component, 'filterContributionsByDate').and.callThrough();
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'Novembro', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'November', day: 15, },
        contributions: []
      }];
      component.minDate = new Date(1);
      component.maxDate = new Date(2022, 12, 25);
      fixture.detectChanges();

      component.filterContributionsByDate(contribs);

      // expectations
      expect(filterSpy).toHaveBeenCalledOnceWith(contribs);
      expect(component.filteredContributionsDateGroups).toEqual(contribs);
    });

    it('T35.3.2 should filter contributions with date range (english app language)', () => {
      let filterSpy = spyOn(component, 'filterContributionsByDate').and.callThrough();
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'Novembro', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'November', day: 15, },
        contributions: []
      }];
      component.minDate = new Date(1);
      component.maxDate = new Date(2022, 12, 25);
      component.language = 'en';
      fixture.detectChanges();

      component.filterContributionsByDate(contribs);

      // expectations
      expect(filterSpy).toHaveBeenCalledOnceWith(contribs);
      expect(component.filteredContributionsDateGroups).toEqual(contribs);
    })

    it('T35.3.3 should add contribution to filtered if month cannot be found (portuguese app language)', () => {
      let filterSpy = spyOn(component, 'filterContributionsByDate').and.callThrough();
      let contribs: ContributionDateGroup[] = [{
        date: {
          year: 2022,
          month: '',
          day: 15,
        },
        contributions: []
      }];
      component.minDate = new Date(1);
      component.maxDate = new Date(2022, 12, 25);
      fixture.detectChanges();

      component.filterContributionsByDate(contribs);

      // expectations
      expect(filterSpy).toHaveBeenCalledOnceWith(contribs);
      expect(component.filteredContributionsDateGroups).toEqual(contribs);
    });

    it('T35.3.4 should add contribution to filtered if month cannot be found (english app language)', () => {
      let filterSpy = spyOn(component, 'filterContributionsByDate').and.callThrough();
      let contribs: ContributionDateGroup[] = [{
        date: {
          year: 2022,
          month: '',
          day: 15,
        },
        contributions: []
      }];
      component.minDate = new Date(1);
      component.maxDate = new Date(2022, 12, 25);
      component.language = 'en';
      fixture.detectChanges();

      component.filterContributionsByDate(contribs);

      // expectations
      expect(filterSpy).toHaveBeenCalledOnceWith(contribs);
      expect(component.filteredContributionsDateGroups).toEqual(contribs);
    });
  });

  describe('TS35.4 Filter contributions by location', () => {
    // location filter
    it('T35.4.1 should receive map for location filtering and set onClick method', () => {
      let receiveSpy = spyOn(component, 'receiveFilterMap').and.callThrough();
      component.showFilterMap = true;
      fixture.detectChanges();
      expect(receiveSpy).toHaveBeenCalled();
      expect(component.filterMap).not.toBeNull();
    });

    it('T35.4.2 should detect click on location filter map', fakeAsync(() => {
      let polylineSpy = spyOn(component, 'createPolyline');
      component.showFilterMap = true;
      fixture.detectChanges();

      // click on map
      let map = fixture.debugElement.query(By.css('#filter-map-geoContrib')).nativeElement;
      map.click();
      tick();

      // expectations
      expect(polylineSpy).toHaveBeenCalled();
    }));

    describe('TS35.4.1 should create visual elements in the filter map on click', () => {
      it('T35.4.1.1 should initialize line group', () => {
        let polylineSpy = spyOn(component, 'createPolyline').and.callThrough();
        let markerSpy = spyOn(component['markerServ'], 'startPolylineGroup');
        let markerAddSpy = spyOn(component['markerServ'], 'addPolylineToFilterMap');
        let coordinates = { lat: 1, long: 1 };

        component.createPolyline(coordinates);

        // expectations
        expect(polylineSpy).toHaveBeenCalledOnceWith(coordinates);
        expect(markerSpy).toHaveBeenCalled();
        expect(markerAddSpy).toHaveBeenCalled();
        expect(component.pointCounter).toBe(1);
      });

      it('T35.4.1.2 should add polygon when last point is added', () => {
        let polylineSpy = spyOn(component, 'createPolyline').and.callThrough();
        let markerAddSpy = spyOn(component['markerServ'], 'addPolylineToFilterMap');
        let markerAddPolygonSpy = spyOn(component['markerServ'], 'addPolygonToFilterMap');
        let coordinates = { lat: 1, long: 1 };

        component.pointCounter = 3;
        fixture.detectChanges();

        component.createPolyline(coordinates);

        // expectations
        expect(polylineSpy).toHaveBeenCalledOnceWith(coordinates);
        expect(markerAddSpy).toHaveBeenCalled();
        expect(markerAddPolygonSpy).toHaveBeenCalled();
        expect(component.pointCounter).toBe(4);
      });

      it('T35.4.1.3 should clear map when clicked after all points are added', () => {
        let polylineSpy = spyOn(component, 'createPolyline').and.callThrough();
        let clearSpy = spyOn(component, 'clearLocFilter');
        let coordinates = { lat: 1, long: 1 };

        component.pointCounter = 4;
        fixture.detectChanges();

        component.createPolyline(coordinates);

        // expectations
        expect(polylineSpy).toHaveBeenCalledOnceWith(coordinates);
        expect(clearSpy).toHaveBeenCalledOnceWith();
      });
    });

    it('T35.4.3 should toggle map when dropdown menu is open/closed', () => {
      let toggleSpy = spyOn(component, 'toggleFilterMap').and.callThrough();
      let fakeElemEmpty = { className: '' } as HTMLDivElement;
      let fakeElemShow = { className: 'show' } as HTMLDivElement;

      component.toggleFilterMap(fakeElemEmpty);
      expect(toggleSpy).toHaveBeenCalledWith(fakeElemEmpty);

      component.toggleFilterMap(fakeElemShow);
      expect(toggleSpy).toHaveBeenCalledWith(fakeElemShow);
      expect(component.pointCounter).toBe(0);
      expect(component.filterPoints).toEqual([]);
    });

    it('T35.4.4 should clear location filter', () => {
      let clearSpy = spyOn(component, 'clearLocFilter').and.callThrough();
      let markerSpy = spyOn(component['markerServ'], 'clearPolyGroup');
      let dateFilterSpy = spyOn(component, 'filterContributionsByDate');

      component.clearLocFilter();

      // expectations
      expect(clearSpy).toHaveBeenCalled();
      expect(component.filterPoints).toEqual([]);
      expect(markerSpy).toHaveBeenCalled();
      expect(dateFilterSpy).toHaveBeenCalled();
    });

    // TODO UPDATE AFTER SOURCE CODE UPDATES
    it('T35.4.5 should filter contributions by location', () => {
      let filterSpy = spyOn(component, 'filterLoc').and.callThrough();
      component.filterPoints = [
        [1, 1],
      ];
      fixture.detectChanges();

      component.filterLoc();

      // expectations
      expect(filterSpy).toHaveBeenCalled();
    });
  });

  describe('TS35.5 Filter contributions by event', () => {
    // event filter
    it('T35.5.1 should search events from events filter list', () => {
      let searchSpy = spyOn(component, 'searchEvents').and.callThrough();
      let fakeEvents = [{ name: 'a' }, { name: 'b' }];
      component.events = fakeEvents;
      fixture.detectChanges();

      component.searchEvents('');
      expect(searchSpy).toHaveBeenCalledWith('');
      expect(component.filteredEvents).toEqual(fakeEvents);

      component.searchEvents('a');
      expect(searchSpy).toHaveBeenCalledWith('a');
      expect(component.filteredEvents).toEqual([{ name: 'a' }]);
    });

    // TODO UPDATE AFTER SOURCE CODE UPDATES
    it('T35.5.2 should filter contributions from selected event', () => {
      let selectSpy = spyOn(component, 'selectEvent').and.callThrough();
      let fakeEvents = [{ id: 1, name: 'a' }, { id: 2, name: 'b' }];
      component.events = fakeEvents;
      component.filteredEvents = fakeEvents;
      fixture.detectChanges();

      component.selectEvent(1);

      // expectations
      expect(selectSpy).toHaveBeenCalled();
      expect(component.events).toEqual([
        { id: 1, name: 'a', selected: true },
        { id: 2, name: 'b', selected: false }
      ]);
      expect(component.filteredEvents).toEqual([
        { id: 1, name: 'a', selected: true },
        { id: 2, name: 'b', selected: false }
      ]);
      expect(component.filterEventName).toEqual('a');
    });
  });

  it('T35.2 should get contribution photo from API', () => {
    let getPhotoSpy = spyOn(component, 'getContribPhoto').and.callThrough();
    let getPhotoServSpy = spyOn(component['contribServ'], 'getContributionPhoto').and.returnValue(of({ data: 'photoData' }));
    component.getContribPhoto('');

    // expectations
    expect(getPhotoSpy).toHaveBeenCalledOnceWith('');
    expect(getPhotoServSpy).toHaveBeenCalledOnceWith('');
    expect(component.contribPhoto).toEqual('data:image/jpg;base64,' + 'photoData');
  });

  it('T35.3 should handle get contribution photo error from API', () => {
    let getPhotoSpy = spyOn(component, 'getContribPhoto').and.callThrough();
    let getPhotoServSpy = spyOn(component['contribServ'], 'getContributionPhoto').and.returnValue(throwError(() => new Error()));

    component.getContribPhoto('');

    // expectations
    expect(getPhotoSpy).toHaveBeenCalledOnceWith('');
    expect(getPhotoServSpy).toHaveBeenCalledOnceWith('');
  });

  it('T35.4 should open contribution photo', () => {
    let modalServiceSpy = spyOn(component['modalService'], 'open').and.callThrough();
    let content: HTMLElement = fixture.debugElement.nativeElement.querySelector('#modal-container');
    component.openContribPhoto(content);
    expect(modalServiceSpy).toHaveBeenCalled();
  });

  it('T35.5 should show all contributions (contributions data)', () => {
    // spies
    let allSpy = spyOn(component, 'allContrib').and.callThrough();
    let toggleSpy = spyOn(component, 'toggleContribButtons');
    let filterSpy = spyOn(component, 'filterContributionsByDate');
    let contribs: ContributionDateGroup[] = [{
      date: { year: 2022, month: 'Novembro', day: 15, },
      contributions: []
    }, {
      date: { year: 2022, month: 'November', day: 15, },
      contributions: []
    }];
    component.allContributionsDateGroups = contribs;
    fixture.detectChanges();

    component.allContrib();

    // expectations
    expect(allSpy).toHaveBeenCalledOnceWith();
    expect(toggleSpy).toHaveBeenCalledOnceWith();
    expect(component.fullContributionsDateGroups).toEqual(component.allContributionsDateGroups);
    expect(component.noContribs).toBeFalse();
    expect(filterSpy).toHaveBeenCalledOnceWith(component.fullContributionsDateGroups);
  });

  it('T35.6 should show all contributions (no contributions data)', () => {
    // spies
    let allSpy = spyOn(component, 'allContrib').and.callThrough();
    let toggleSpy = spyOn(component, 'toggleContribButtons');
    let filterSpy = spyOn(component, 'filterContributionsByDate');

    component.allContrib();

    // expectations
    expect(allSpy).toHaveBeenCalledOnceWith();
    expect(toggleSpy).toHaveBeenCalledOnceWith();
    expect(component.fullContributionsDateGroups).toEqual(component.allContributionsDateGroups);
    expect(component.noContribs).toBeTrue();
    expect(filterSpy).toHaveBeenCalledOnceWith(component.fullContributionsDateGroups);
  });

  it('T35.7 should show user contributions (contributions data)', () => {
    // spies
    let userSpy = spyOn(component, 'myContrib').and.callThrough();
    let toggleSpy = spyOn(component, 'toggleContribButtons');
    let filterSpy = spyOn(component, 'filterContributionsByDate');
    let contribs: ContributionDateGroup[] = [{
      date: { year: 2022, month: 'Novembro', day: 15, },
      contributions: []
    }, {
      date: { year: 2022, month: 'November', day: 15, },
      contributions: []
    }];
    component.userContributionsDateGroups = contribs;
    fixture.detectChanges();

    component.myContrib();

    // expectations
    expect(userSpy).toHaveBeenCalledOnceWith();
    expect(toggleSpy).toHaveBeenCalledOnceWith();
    expect(component.fullContributionsDateGroups).toEqual(component.userContributionsDateGroups);
    expect(component.noContribs).toBeFalse();
    expect(filterSpy).toHaveBeenCalledOnceWith(component.fullContributionsDateGroups);
  });

  it('T35.8 should show user contributions (no contributions data)', () => {
    // spies
    let userSpy = spyOn(component, 'myContrib').and.callThrough();
    let toggleSpy = spyOn(component, 'toggleContribButtons');
    let filterSpy = spyOn(component, 'filterContributionsByDate');

    component.myContrib();

    // expectations
    expect(userSpy).toHaveBeenCalledOnceWith();
    expect(toggleSpy).toHaveBeenCalledOnceWith();
    expect(component.fullContributionsDateGroups).toEqual(component.userContributionsDateGroups);
    expect(component.noContribs).toBeTrue();
    expect(filterSpy).toHaveBeenCalledOnceWith(component.fullContributionsDateGroups);
  });

  it('T35.9 should open contribution', () => {
    // spies and setup
    let openSpy = spyOn(component, 'openContribution').and.callThrough();
    let photoSpy = spyOn(component, 'getContribPhoto');
    let contrib: Contribution = {
      fid: 0,
      pic: 'pic url',
      location: 'location',
      date: {
        year: 2022,
        month: 11,
        day: 15
      },
      hour: '10',
      minute: '20',
      geom: [{ pid: 1, lat: 10, long: 10 }, { pid: 2, lat: 10, long: 10 }],
      dir: 0,
      dsun: null,
    };
    let index = 1;

    component.openContribution(contrib, index);

    // expectations
    expect(openSpy).toHaveBeenCalledOnceWith(contrib, index);
    expect(component.isContribOpen).toBeTrue();
    expect(component.contribIndex).toBe(index);
    expect(photoSpy).toHaveBeenCalledOnceWith(contrib.pic);
    expect(component.contribId).toBe(contrib.fid);
    expect(component.contribLocation).toBe(contrib.location);
    expect(component.contribTime).toEqual(contrib.hour + ':' + contrib.minute);
    expect(component.contribDirection).toBe(contrib.dir);
  });

  it('T35.10 should open contribution with optional data', () => {
    // spies and setup
    let openSpy = spyOn(component, 'openContribution').and.callThrough();
    let photoSpy = spyOn(component, 'getContribPhoto');
    let contrib: Contribution = {
      fid: 0,
      pic: 'pic url',
      location: 'location',
      date: {
        year: 2022,
        month: 11,
        day: 15
      },
      hour: '10',
      minute: '20',
      geom: [{ pid: 1, lat: 10, long: 10 }, { pid: 2, lat: 10, long: 10 }],
      dir: 0,
      dsun: 2,
    };
    let index = 1;

    component.openContribution(contrib, index);

    // expectations
    expect(openSpy).toHaveBeenCalledOnceWith(contrib, index);
    expect(component.isContribOpen).toBeTrue();
    expect(component.contribIndex).toBe(index);
    expect(photoSpy).toHaveBeenCalledOnceWith(contrib.pic);
    expect(component.contribId).toBe(contrib.fid);
    expect(component.contribLocation).toBe(contrib.location);
    expect(component.contribTime).toEqual(contrib.hour + ':' + contrib.minute);
    expect(component.contribDirection).toBe(contrib.dir);
    expect(component.contribSun).toEqual(contrib.dsun);
  });

  it('T35.11 should close contribution if clicked on list contribution while open', () => {
    // spies and setup
    let openSpy = spyOn(component, 'openContribution').and.callThrough();
    let closeSpy = spyOn(component, 'closeContribution').and.callThrough();
    let contrib: Contribution = {
      fid: 0,
      pic: 'pic url',
      location: 'location',
      date: {
        year: 2022,
        month: 11,
        day: 15
      },
      hour: '10',
      minute: '20',
      geom: [{ pid: 1, lat: 10, long: 10 }, { pid: 2, lat: 10, long: 10 }],
      dir: 0,
      dsun: 2,
    };
    let index = 1;
    component.contribId = 0;
    fixture.detectChanges();

    component.openContribution(contrib, index);

    // expectations
    expect(openSpy).toHaveBeenCalledOnceWith(contrib, index);
    expect(closeSpy).toHaveBeenCalledOnceWith();
    expect(component.contribId).toBe(-1);
    expect(component.contribIndex).toBe(-1);
    expect(component.isContribOpen).toBeFalse();
  });

  it('T35.12 should close contribution', () => {
    let closeSpy = spyOn(component, 'closeContribution').and.callThrough();
    component.closeContribution();

    // expectations
    expect(closeSpy).toHaveBeenCalledOnceWith();
    expect(component.contribId).toBe(-1);
    expect(component.contribIndex).toBe(-1);
    expect(component.isContribOpen).toBeFalse();
  });

  it('T35.13 should toggle contribution buttons', () => {
    expect(component.allContribSelected).toBeTrue();
    component.toggleContribButtons();
    expect(component.allContribSelected).toBeFalse();
    component.toggleContribButtons();
    expect(component.allContribSelected).toBeTrue();
  });

  it('T35.14 should open login modal', () => {
    let modalServiceSpy = spyOn(component['modalService'], 'open').and.callThrough();
    component.openLogin();
    expect(modalServiceSpy).toHaveBeenCalled();
  });

  it('T35.15 should open register modal', () => {
    let modalServiceSpy = spyOn(component['modalService'], 'open').and.callThrough();
    component.openRegister();
    expect(modalServiceSpy).toHaveBeenCalled();
  });

  describe('TS35.6 Group contributions by date', () => {
    it('T35.6.1 should check if date has been added to contribution array', () => {
      // spies and setup
      let contribGroups: ContributionDateGroup[] = [{
        date: { year: 2022, month: 11, day: 14 }, contributions: []
      }];
      let dateExists: ContribDate = { year: 2022, month: 11, day: 14 };
      let dateNot: ContribDate = { year: 2021, month: 11, day: 14 };
      let checkSpy = spyOn(component, 'checkDateAdded').and.callThrough();

      // calls
      let added = component.checkDateAdded(dateExists, contribGroups);
      let notAdded = component.checkDateAdded(dateNot, contribGroups);

      // expectations
      expect(checkSpy).toHaveBeenCalledTimes(2);
      expect(added).toBeTrue();
      expect(notAdded).toBeFalse();
    });

    it('T35.6.2 should group contributions by date [all contributions, add to group]', () => {
      // setup
      let groupSpy = spyOn(component, 'groupContribByDate').and.callThrough();
      let checkSpy = spyOn(component, 'checkDateAdded').and.returnValue(false);
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');
      let userActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');
      let contribs: Contribution[] = [
        {
          fid: 1, pic: '', location: '', date: { year: 2022, month: 'Novembro', day: 15, },
          hour: 4, minute: 13, geom: [], dir: 1, dsun: 1
        },
        {
          fid: 2, pic: '', location: '', date: { year: 2021, month: 'Novembro', day: 15, },
          hour: 4, minute: 13, geom: [], dir: 1, dsun: 1
        },
      ];

      component.groupContribByDate(contribs, 'all');

      // expectations
      expect(groupSpy).toHaveBeenCalledOnceWith(contribs, 'all');
      expect(checkSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalledOnceWith(component.allContributionsDateGroups);
      expect(userActionSpy).not.toHaveBeenCalled();
    });

    it('T35.6.3 should group contributions by date [all contributions, don\'t add to group]', () => {
      // setup
      let groupSpy = spyOn(component, 'groupContribByDate').and.callThrough();
      let checkSpy = spyOn(component, 'checkDateAdded').and.returnValue(true);
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');
      let userActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');
      let contribs: Contribution[] = [
        {
          fid: 1, pic: '', location: '', date: { year: 2022, month: '', day: 15, },
          hour: 4, minute: 13, geom: [], dir: 1, dsun: 1
        },
        {
          fid: 2, pic: '', location: '', date: { year: 2021, month: '', day: 15, },
          hour: 4, minute: 13, geom: [], dir: 1, dsun: 1
        },
      ];

      component.groupContribByDate(contribs, 'all');

      // expectations
      expect(groupSpy).toHaveBeenCalledOnceWith(contribs, 'all');
      expect(checkSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalledOnceWith(component.allContributionsDateGroups);
      expect(userActionSpy).not.toHaveBeenCalled();
    });

    it('T35.6.4 should group contributions by date [user contributions, add to group]', () => {
      // setup
      let groupSpy = spyOn(component, 'groupContribByDate').and.callThrough();
      let checkSpy = spyOn(component, 'checkDateAdded').and.returnValue(false);
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');
      let userActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');
      let contribs: Contribution[] = [
        {
          fid: 1, pic: '', location: '', date: { year: 2022, month: 'Novembro', day: 15, },
          hour: 4, minute: 13, geom: [], dir: 1, dsun: 1
        },
        {
          fid: 2, pic: '', location: '', date: { year: 2021, month: 'Novembro', day: 15, },
          hour: 4, minute: 13, geom: [], dir: 1, dsun: 1
        },
      ];

      component.groupContribByDate(contribs, 'user');

      // expectations
      expect(groupSpy).toHaveBeenCalledOnceWith(contribs, 'user');
      expect(checkSpy).toHaveBeenCalled();
      expect(allActionSpy).not.toHaveBeenCalled();
      expect(userActionSpy).toHaveBeenCalledOnceWith(component.userContributionsDateGroups);
    });

    it('T35.6.5 should group contributions by date [user contributions, don\'t add to group]', () => {
      // setup
      let groupSpy = spyOn(component, 'groupContribByDate').and.callThrough();
      let checkSpy = spyOn(component, 'checkDateAdded').and.returnValue(true);
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');
      let userActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');
      let contribs: Contribution[] = [
        {
          fid: 1, pic: '', location: '', date: { year: 2022, month: '', day: 15, },
          hour: 4, minute: 13, geom: [], dir: 1, dsun: 1
        },
        {
          fid: 2, pic: '', location: '', date: { year: 2021, month: '', day: 15, },
          hour: 4, minute: 13, geom: [], dir: 1, dsun: 1
        },
      ];

      component.groupContribByDate(contribs, 'user');

      // expectations
      expect(groupSpy).toHaveBeenCalledOnceWith(contribs, 'user');
      expect(checkSpy).toHaveBeenCalled();
      expect(allActionSpy).not.toHaveBeenCalled();
      expect(userActionSpy).toHaveBeenCalledOnceWith(component.userContributionsDateGroups);
    });

    it('T35.6.6 should not group contributions by date if parameter is unexpected', () => {
      // setup
      let groupSpy = spyOn(component, 'groupContribByDate').and.callThrough();
      let checkSpy = spyOn(component, 'checkDateAdded').and.returnValue(true);
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');
      let userActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');
      let contribs: Contribution[] = [
        {
          fid: 1, pic: '', location: '', date: { year: 2022, month: '', day: 15, },
          hour: 4, minute: 13, geom: [], dir: 1, dsun: 1
        },
        {
          fid: 2, pic: '', location: '', date: { year: 2021, month: '', day: 15, },
          hour: 4, minute: 13, geom: [], dir: 1, dsun: 1
        },
      ];

      component.groupContribByDate(contribs, '');

      // expectations
      expect(groupSpy).toHaveBeenCalledOnceWith(contribs, '');
      expect(checkSpy).not.toHaveBeenCalled();
      expect(allActionSpy).not.toHaveBeenCalled();
      expect(userActionSpy).not.toHaveBeenCalledOnceWith(component.userContributionsDateGroups);
    });
  });

  describe('TS35.7 Sort contributions by date', () => {
    it('T35.7.1 all contributions (portuguese app language, portuguese months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'Novembro', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'Novembro', day: 15, },
        contributions: []
      }];
      component.allContributionsDateGroups = contribs;
      component.language = 'pt';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');

      component.sortContribByDate('all');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.2 all contributions (portuguese app language, english months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'November', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'November', day: 15, },
        contributions: []
      }];
      component.allContributionsDateGroups = contribs;
      component.language = 'pt';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');

      component.sortContribByDate('all');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.3 all contributions (portuguese app language, unknown months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'fake', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'fake', day: 15, },
        contributions: []
      }];
      component.allContributionsDateGroups = contribs;
      component.language = 'pt';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');

      component.sortContribByDate('all');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.4 all contributions (english app language, english months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'November', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'November', day: 15, },
        contributions: []
      }];
      component.allContributionsDateGroups = contribs;
      component.language = 'en';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');

      component.sortContribByDate('all');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.5 all contributions (english app language, portuguese months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'Novembro', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'Novembro', day: 15, },
        contributions: []
      }];
      component.allContributionsDateGroups = contribs;
      component.language = 'en';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');

      component.sortContribByDate('all');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.6 all contributions (english app language, unknown months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'fake', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'fake', day: 15, },
        contributions: []
      }];
      component.allContributionsDateGroups = contribs;
      component.language = 'en';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveAllContributions');

      component.sortContribByDate('all');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.7 user contributions (portuguese app language, portuguese months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'Novembro', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'Novembro', day: 15, },
        contributions: []
      }];
      component.userContributionsDateGroups = contribs;
      component.language = 'pt';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');

      component.sortContribByDate('user');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.8 user contributions (portuguese app language, english months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'November', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'November', day: 15, },
        contributions: []
      }];
      component.userContributionsDateGroups = contribs;
      component.language = 'pt';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');

      component.sortContribByDate('user');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.9 user contributions (portuguese app language, unknown months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'fake', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'fake', day: 15, },
        contributions: []
      }];
      component.userContributionsDateGroups = contribs;
      component.language = 'pt';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');

      component.sortContribByDate('user');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.10 user contributions (english app language, english months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'November', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'November', day: 15, },
        contributions: []
      }];
      component.userContributionsDateGroups = contribs;
      component.language = 'en';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');

      component.sortContribByDate('user');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.11 user contributions (english app language, portuguese months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'Novembro', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'Novembro', day: 15, },
        contributions: []
      }];
      component.userContributionsDateGroups = contribs;
      component.language = 'en';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');

      component.sortContribByDate('user');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });

    it('T35.7.12 user contributions (english app language, unknown months)', () => {
      let contribs: ContributionDateGroup[] = [{
        date: { year: 2022, month: 'fake', day: 15, },
        contributions: []
      }, {
        date: { year: 2022, month: 'fake', day: 15, },
        contributions: []
      }];
      component.userContributionsDateGroups = contribs;
      component.language = 'en';
      fixture.detectChanges();

      let sortSpy = spyOn(component, 'sortContribByDate').and.callThrough();
      let allActionSpy = spyOn(component['contributionActions'], 'saveUserContributions');

      component.sortContribByDate('user');

      expect(sortSpy).toHaveBeenCalled();
      expect(allActionSpy).toHaveBeenCalled();
    });
  });

});
