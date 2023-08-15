import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';
import { ChangeContext, NgxSliderModule, PointerType } from '@angular-slider/ngx-slider';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DateRangeActions } from 'src/app/redux/actions/dateRangeActions';
import { INITIAL_STATE_CONTRIB } from 'src/app/redux/reducers/contributionReducer';
import { INITIAL_STATE_EVENT } from 'src/app/redux/reducers/eventReducer';
import { INITIAL_STATE_LANG } from 'src/app/redux/reducers/langReducer';
import { selectContribution, selectEvent, selectLanguage } from 'src/app/redux/selectors';

import { MapFooterComponent } from './map-footer.component';

describe('TS32 MapFooterComponent', () => {
  let component: MapFooterComponent;
  let fixture: ComponentFixture<MapFooterComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MapFooterComponent],
      imports: [
        NgReduxTestingModule,
        HttpClientTestingModule,
        NgxSliderModule,
      ],
      providers: [
        DateRangeActions
      ]
    }).compileComponents();

    // reset redux
    MockNgRedux.reset();

    fixture = TestBed.createComponent(MapFooterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T32.1 should create', () => { expect(component).toBeTruthy(); });

  it('T32.2 should check if HTML container is null', () => {
    let initSpy = spyOn(component, 'ngOnInit').and.callThrough();
    spyOn(document, 'getElementById').and.returnValue(null);
    component.ngOnInit();
    expect(initSpy).toHaveBeenCalled();
  });

  describe('TS32.1 Redux subscriptions', () => {
    it('T32.1.1 should subscribe to redux for contributions (no contributions)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let updateSpy = spyOn(component, 'updateDateRange');

      // select all contribs state and initialize
      const contribStub = MockNgRedux.getSelectorStub(selectContribution);
      contribStub.next(INITIAL_STATE_CONTRIB);
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.contributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_CONTRIB);
          expect(updateSpy).not.toHaveBeenCalled();
        }
      );
    });

    it('T32.1.2 should subscribe to redux for contributions (all contributions)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let updateSpy = spyOn(component, 'updateDateRange');

      // select all contribs state and initialize
      const contribStub = MockNgRedux.getSelectorStub(selectContribution);
      contribStub.next({
        allContributions: [{
          date: { year: 2022, month: 12, day: 18 }, contributions: []
        }], userContributions: []
      });
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.contributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected   
          expect(component.allContributionsDateGroups).toEqual([{
            date: { year: 2022, month: 12, day: 18 }, contributions: []
          }]);
          expect(updateSpy).toHaveBeenCalled();
        }
      );
    });

    it('T32.1.3 should subscribe to redux for contributions (user contributions)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let updateSpy = spyOn(component, 'updateDateRange');

      // select all contribs state and initialize
      const contribStub = MockNgRedux.getSelectorStub(selectContribution);
      contribStub.next({
        userContributions: [{
          date: { year: 2022, month: 12, day: 18 }, contributions: []
        }], allContributions: []
      });
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.contributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected   
          expect(component.userContributionsDateGroups).toEqual([{
            date: { year: 2022, month: 12, day: 18 }, contributions: []
          }]);
          expect(updateSpy).toHaveBeenCalled();
        }
      );
    });

    it('T32.1.4 should subscribe to redux for events (no events)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let updateSpy = spyOn(component, 'updateDateRange');

      // select all contribs state and initialize
      const contribStub = MockNgRedux.getSelectorStub(selectEvent);
      contribStub.next(INITIAL_STATE_EVENT);
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.contributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_EVENT);
          expect(updateSpy).not.toHaveBeenCalled();
        }
      );
    });

    it('T32.1.5 should subscribe to redux for events (events)', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let updateSpy = spyOn(component, 'updateDateRange');

      // select all contribs state and initialize
      const contribStub = MockNgRedux.getSelectorStub(selectEvent);
      contribStub.next({
        events: [{
          id: 1, nearPlace: 1, place: { fregID: 1, geom: '', id: 1, name: '', lugID: 1 },
          startTime: { year: 1, month: 1, day: 1, hour: 1, minute: 1 },
          endTime: { year: 1, month: 1, day: 1, hour: 1, minute: 1 },
          contribStart: { year: 1, month: 1, day: 1, hour: 1, minute: 1 },
          contribEnd: { year: 1, month: 1, day: 1, hour: 1, minute: 1 },
          contributionPhotos: [], attributes: [], layers: []
        }],
        serviceLayers: []
      });
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.contributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected   
          expect(component.firelocEvents).toEqual(actualInfo.events);
          expect(updateSpy).toHaveBeenCalled();
        }
      );
    });

    it('T32.1.6 should subscribe to redux for app language', () => {
      // spies
      let reduxSubSpy = spyOn(component, 'subscribeToRedux');
      let updateSpy = spyOn(component, 'updateDateRange');

      // select all contribs state and initialize
      const contribStub = MockNgRedux.getSelectorStub(selectLanguage);
      contribStub.next(INITIAL_STATE_LANG.language);
      contribStub.complete();

      component.subscribeToRedux();

      // expectations
      expect(reduxSubSpy).toHaveBeenCalledOnceWith();
      component.contributions$.subscribe(
        (actualInfo: any) => {
          // user info received should be as expected        
          expect(actualInfo).toEqual(INITIAL_STATE_LANG.language);
          expect(component.language).toEqual(INITIAL_STATE_LANG.language);
          expect(updateSpy).toHaveBeenCalled();
        }
      );
    });
  });

  it('T32.3 should update date range', () => {
    // setup
    let createSpy = spyOn(component, 'createDateRange').and.callThrough();
    let sliderSpy = spyOn(component, 'updateSliderRange');
    let actionsSpy = spyOn(component['dateRangeActions'], 'updateValues');

    component.minValue = 10;
    component.maxValue = 20;
    fixture.detectChanges();

    component.updateDateRange();

    // expectations
    expect(createSpy).toHaveBeenCalled();
    expect(sliderSpy).toHaveBeenCalled();
    expect(actionsSpy).toHaveBeenCalled();
  });

  describe('TS32.2 Create date range', () => {
    it('T32.2.1 should create default date range', () => {
      let dates = component.createDateRange();
      expect(component.allContributionsDateGroups.length).toBe(0);
      expect(component.userContributionsDateGroups.length).toBe(0);
      expect(component.firelocEvents.length).toBe(0);
      expect(dates.length).toBe(32);
    });

    it('T32.2.2 should create date range from events', () => {
      component.firelocEvents = [{
        id: 1, startTime: { year: 2022, month: 8, day: 10, hour: 0, minute: 0 }, endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: ['', ''], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      }, {
        id: 2, startTime: { year: 2022, month: '8', day: 10, hour: 0, minute: 0 }, endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: ['', ''], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      }]
      let dates = component.createDateRange();
      expect(component.allContributionsDateGroups.length).toBe(0);
      expect(component.userContributionsDateGroups.length).toBe(0);
      expect(component.firelocEvents.length).toBe(2);
      expect(dates.length).toBe(1);
    });

    it('T32.2.3 should create date range from all contributions', () => {
      component.allContributionsDateGroups = [{
        date: { year: 2022, month: 'January', day: 1 }, contributions: []
      }, {
        date: { year: 2022, month: 'January', day: 10 }, contributions: []
      }, {
        date: { year: 2022, month: 1, day: 10 }, contributions: []
      }]
      let dates = component.createDateRange();
      expect(component.allContributionsDateGroups.length).toBe(3);
      expect(component.userContributionsDateGroups.length).toBe(0);
      expect(component.firelocEvents.length).toBe(0);
      expect(dates.length).toBe(2);
    });

    it('T32.2.4 should create date range from user contributions', () => {
      component.userContributionsDateGroups = [{
        date: { year: 2022, month: 'January', day: 1 }, contributions: []
      }, {
        date: { year: 2022, month: 'January', day: 10 }, contributions: []
      }, {
        date: { year: 2022, month: 1, day: 10 }, contributions: []
      }]
      let dates = component.createDateRange();
      expect(component.allContributionsDateGroups.length).toBe(0);
      expect(component.userContributionsDateGroups.length).toBe(3);
      expect(component.firelocEvents.length).toBe(0);
      expect(dates.length).toBe(2);
    });

    it('T32.2.5 should create date range from events and all contributions', () => {
      component.firelocEvents = [{
        id: 1, startTime: { year: 2022, month: 8, day: 10, hour: 0, minute: 0 }, endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: ['', ''], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      }, {
        id: 2, startTime: { year: 2022, month: '8', day: 10, hour: 0, minute: 0 }, endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: ['', ''], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      }];
      component.allContributionsDateGroups = [{
        date: { year: 2022, month: 'January', day: 1 }, contributions: []
      }, {
        date: { year: 2022, month: 'January', day: 10 }, contributions: []
      }, {
        date: { year: 2022, month: 1, day: 10 }, contributions: []
      }];
      let dates = component.createDateRange();
      expect(component.allContributionsDateGroups.length).toBe(3);
      expect(component.userContributionsDateGroups.length).toBe(0);
      expect(component.firelocEvents.length).toBe(2);
      expect(dates.length).toBe(3);
    });

    it('T32.2.6 should create date range from events and user contributions', () => {
      component.firelocEvents = [{
        id: 1, startTime: { year: 2022, month: 8, day: 10, hour: 0, minute: 0 }, endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: ['', ''], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      }, {
        id: 2, startTime: { year: 2022, month: '8', day: 10, hour: 0, minute: 0 }, endTime: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribStart: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        contribEnd: { year: 0, month: 0, day: 0, hour: 0, minute: 0 },
        nearPlace: 0, contributionPhotos: ['', ''], layers: [], attributes: [],
        place: { id: 1, fregID: 1, lugID: 1, geom: '', name: '' },
      }];
      component.userContributionsDateGroups = [{
        date: { year: 2022, month: 'January', day: 1 }, contributions: []
      }, {
        date: { year: 2022, month: 'January', day: 10 }, contributions: []
      }, {
        date: { year: 2022, month: 1, day: 10 }, contributions: []
      }];
      let dates = component.createDateRange();
      expect(component.allContributionsDateGroups.length).toBe(0);
      expect(component.userContributionsDateGroups.length).toBe(3);
      expect(component.firelocEvents.length).toBe(2);
      expect(dates.length).toBe(3);
    });
  });

  it('T32.4 should update slider range', () => {
    component.sliderTickWidth = 0;
    component.updateSliderRange();
    expect(component.sliderWidth).toBe(700);
  });

  it('T32.5 should change minimum and maximum date values on user change end', () => {
    let changeContext: ChangeContext = { value: 10, highValue: 20, pointerType: PointerType.Min };
    let actionSpy = spyOn(component['dateRangeActions'], 'updateValues');

    component.onUserChangeEnd(changeContext);

    changeContext = { value: 10, pointerType: PointerType.Min };
    component.onUserChangeEnd(changeContext);

    expect(actionSpy).toHaveBeenCalledTimes(1);
  });

  it('T32.6 should translate month string into value (portuguese app language)', () => {
    component.language = 'pt';
    let ptMonth = component.translateMonthString('Janeiro');
    expect(ptMonth).toBe(0);

    let enMonth = component.translateMonthString('January');
    expect(enMonth).toBe(0);

    let unkMonth = component.translateMonthString('nope');
    expect(unkMonth).toBe(-1);
  });

  it('T32.7 should translate month string into value (english app language)', () => {
    component.language = 'en';
    let ptMonth = component.translateMonthString('Janeiro');
    expect(ptMonth).toBe(0);

    let enMonth = component.translateMonthString('January');
    expect(enMonth).toBe(0);

    let unkMonth = component.translateMonthString('nope');
    expect(unkMonth).toBe(-1);
  });

  it('T32.8 should start to drag slider', () => {
    let e = { pageX: 2 };
    let el = { offsetLeft: 1, scrollLeft: 1 };
    component.startDragging(e, el);
    expect(component.mouseDown).toBeTrue();
    expect(component.startX).toBe(1);
    expect(component.scrollLeft).toBe(1);
  });

  it('T32.9 should stop dragging slider', () => {
    component.stopDragging();
    expect(component.mouseDown).toBeFalse();
  });

  it('T32.10 should detect move event (mouse up)', () => {
    let e = { pageX: 2, preventDefault: () => { } };
    let el = { offsetLeft: 1, scrollLeft: 1 };
    component.mouseDown = false;
    component.moveEvent(e, el);
    expect(component.mouseDown).toBeFalse();
  });

  it('T32.11 should detect move event (mouse down)', () => {
    let e = { pageX: 2, preventDefault: () => { } };
    let el = { offsetLeft: 1, scrollLeft: 1 };
    component.mouseDown = true;
    component.moveEvent(e, el);
    expect(component.mouseDown).toBeTrue();
  });

  it('T32.12 should update slider zoom', ()=>{
    spyOn(component, 'updateSliderRange');
    
    let e = 20;
    component.updateSliderZoom(e);
    expect(component.sliderTickWidth).toBe(38);

    e = -2000;
    component.updateSliderZoom(e);
    expect(component.sliderTickWidth).toBe(100);
  });

});
