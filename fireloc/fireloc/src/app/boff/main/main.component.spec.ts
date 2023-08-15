import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NavigationEnd, NavigationStart, Router, RouterEvent } from '@angular/router';
import { ReplaySubject } from 'rxjs';
import { SidebarConstants } from 'src/app/constants/boffNav';

import { MainComponent } from './main.component';

// Mock Router
const eventSubject = new ReplaySubject<RouterEvent>(2);
const routerMock = {
  url: 'admin/home',
  events: eventSubject.asObservable(),
  navigate: jasmine.createSpy('navigate'),
};

describe('TS16 Backoffice MainComponent', () => {
  let component: MainComponent;
  let fixture: ComponentFixture<MainComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MainComponent],
      schemas: [NO_ERRORS_SCHEMA],
      providers: [{ provide: Router, useValue: routerMock },]
    }).compileComponents();

    fixture = TestBed.createComponent(MainComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T16.1 should create', () => { expect(component).toBeTruthy(); });

  it('T16.2 should call check url on Navigation End event', () => {
    let checkUrlSpy = spyOn(component, 'checkUrl');

    eventSubject.next(new NavigationStart(1, 'url'));
    eventSubject.next(new NavigationEnd(2, 'url', '/admin/home'));
    expect(checkUrlSpy).toHaveBeenCalledTimes(1);
  });

  it('T16.3 should correctly check url', () => {
    // spies
    const checkUrlSpy = spyOn(component, 'checkUrl').and.callThrough();
    //const routerUrlSpy = spyOnProperty(router, 'url', 'get');

    // initial value
    expect(component.activePage).toBe(0);

    // users
    let url = SidebarConstants.usersLinks[0].url;
    component.checkUrl(url); expect(component.activePage).toBe(1);

    // groups
    url = SidebarConstants.usersLinks[1].url;
    component.checkUrl(url); expect(component.activePage).toBe(2);

    // contributions
    url = SidebarConstants.contribLinks[0].url;
    component.checkUrl(url); expect(component.activePage).toBe(3);

    // events
    url = SidebarConstants.contribLinks[1].url;
    component.checkUrl(url); expect(component.activePage).toBe(4);

    // real events
    url = SidebarConstants.otherLinks[0].url;
    component.checkUrl(url); expect(component.activePage).toBe(5);

    // layers
    url = SidebarConstants.mapLinks[0].url;
    component.checkUrl(url); expect(component.activePage).toBe(6);

    // legend
    url = SidebarConstants.mapLinks[1].url;
    component.checkUrl(url); expect(component.activePage).toBe(7);

    // graph
    url = SidebarConstants.mapLinks[2].url;
    component.checkUrl(url); expect(component.activePage).toBe(8);

    // satellite
    url = SidebarConstants.geosLinks[0].url;
    component.checkUrl(url); expect(component.activePage).toBe(9);

    // raster
    url = SidebarConstants.geosLinks[1].url;
    component.checkUrl(url); expect(component.activePage).toBe(10);

    // vetorial
    url = SidebarConstants.geosLinks[2].url;
    component.checkUrl(url); expect(component.activePage).toBe(11);

    // home (default)
    url = 'admin/home';
    component.checkUrl(url); expect(component.activePage).toBe(0);

    // all method calls
    expect(checkUrlSpy).toHaveBeenCalledTimes(12);

  });
});
