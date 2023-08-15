// Testing
import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { NgReduxTestingModule } from '@angular-redux/store/testing';

// Modules
import { NavigationEnd, NavigationStart, Router, RouterEvent } from '@angular/router';
import { By } from '@angular/platform-browser';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

// Routes
import { SidebarConstants } from 'src/app/constants/boffNav';

// Components
import { SideNavComponent } from './side-nav.component';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';
import { UserService } from 'src/app/serv/rest/users/user.service';

// Redux
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';

// Guards
import { AuthGuard } from 'src/app/auth/guards/auth.guard';
import { RoleGuard } from 'src/app/auth/guards/role.guard';

// Other
import { of, ReplaySubject, throwError } from 'rxjs';
import { Directive, Input, HostListener } from '@angular/core';

// Mock RouterLink (to remove warnings)
@Directive({
  selector: '[routerLink]',
})
export class RouterLinkStubDirective {
  @Input('routerLink') linkParams: any;
  navigatedTo: any;

  @HostListener('click') onClick(): void {
    this.navigatedTo = this.linkParams;
  }
}

// Mock Router
const eventSubject = new ReplaySubject<RouterEvent>(2);
const routerMock = {
  url: 'admin/home',
  events: eventSubject.asObservable(),
  navigate: jasmine.createSpy('navigate'),
};

describe('TS25 SideNavComponent', () => {
  let component: SideNavComponent;
  let fixture: ComponentFixture<SideNavComponent>;

  beforeEach(() => {
    // mock guard
    const canActivateStub = () => ({ canActivate: () => true });

    TestBed.configureTestingModule({
      declarations: [SideNavComponent, RouterLinkStubDirective],
      imports: [
        /* RouterModule, */
        /* RouterTestingModule, */
        FontAwesomeModule,
        HttpClientTestingModule,
        NgReduxTestingModule,
      ],
      providers: [
        AuthService,
        UserService,
        ContributionActions,
        EventActions,
        { provide: AuthGuard, useValue: canActivateStub },
        { provide: RoleGuard, useValue: canActivateStub },
        { provide: Router, useValue: routerMock },

      ]
    }).compileComponents();

    // component for testing
    fixture = TestBed.createComponent(SideNavComponent);
    component = fixture.componentInstance;

    // trigger initial data binding
    fixture.detectChanges();

    // find DebugElements with an attached RouterLinkStubDirective
    const linkDes = fixture.debugElement.queryAll(By.directive(RouterLinkStubDirective));
    // get attached link directive instances using each DebugElement's injector
    const routerLinks = linkDes.map(de => de.injector.get(RouterLinkStubDirective));

  });

  it('T25.1 should create', () => {
    expect(component).toBeTruthy();
  });

  it('T25.2 should call check url on Navigation End event', () => {
    let checkUrlSpy = spyOn(component, 'checkUrl');

    eventSubject.next(new NavigationStart(1, 'url'));
    eventSubject.next(new NavigationEnd(2, 'url', '/admin/home'));
    expect(checkUrlSpy).toHaveBeenCalledTimes(1);
  });

  it('T25.3 should call #toggleSideNav on collapse icon click', () => {
    const toggleNavSpy = spyOn(component, 'toggleSideNav');

    // icon element click
    let iconEl = fixture.debugElement.query(By.css('.arrow')).nativeElement;
    iconEl.click();

    expect(toggleNavSpy).toHaveBeenCalled();
  });

  it('T25.4 should collapse/expand side nav bar', () => {
    const toggleNavSpy = spyOn(component, 'toggleSideNav').and.callThrough();

    // initial value
    expect(component.isNavCollapsed).toBeFalse;

    // close nav
    component.toggleSideNav();
    expect(toggleNavSpy).toHaveBeenCalled();
    expect(component.isNavCollapsed).toBeTrue;

    // open nav again
    component.toggleSideNav();
    expect(toggleNavSpy).toHaveBeenCalled();
    expect(component.isNavCollapsed).toBeFalse;
  });

  it('T25.5 should call #openGeoMenu on menu click', () => {
    const geoMenuSpy = spyOn(component, 'openGeoMenu');

    // menu element click on open nav
    let geoMenuOpenEl = fixture.debugElement.queryAll(By.css('.nav-item'))[8].nativeElement;
    geoMenuOpenEl.click();
    expect(geoMenuSpy).toHaveBeenCalled();

    // menu element click on closed nav
    component.isNavCollapsed = true;
    fixture.detectChanges();
    geoMenuOpenEl.click();
    expect(geoMenuSpy).toHaveBeenCalled();
  });

  it('T25.6 should collapse/expand geo menu', () => {
    const geoMenuSpy = spyOn(component, 'openGeoMenu').and.callThrough();

    // initial value
    expect(component.isGeoMenuOpen).toBeFalse;

    // open menu
    component.openGeoMenu();
    expect(geoMenuSpy).toHaveBeenCalled();
    expect(component.isGeoMenuOpen).toBeTrue;

    // close menu again
    component.openGeoMenu();
    expect(geoMenuSpy).toHaveBeenCalled();
    expect(component.isGeoMenuOpen).toBeFalse;
  });

  it('T25.7 should correctly check url', () => {
    // spies
    const checkUrlSpy = spyOn(component, 'checkUrl').and.callThrough();
    //const routerUrlSpy = spyOnProperty(router, 'url', 'get');

    // initial value
    expect(component.activeNavItem).toBe(0);

    // users
    routerMock.url = SidebarConstants.usersLinks[0].url;
    component.checkUrl(); expect(component.activeNavItem).toBe(1);

    // groups
    routerMock.url = SidebarConstants.usersLinks[1].url;
    component.checkUrl(); expect(component.activeNavItem).toBe(2);

    // contributions
    routerMock.url = SidebarConstants.contribLinks[0].url;
    component.checkUrl(); expect(component.activeNavItem).toBe(3);

    // events
    routerMock.url = SidebarConstants.contribLinks[1].url;
    component.checkUrl(); expect(component.activeNavItem).toBe(4);

    // real events
    routerMock.url = SidebarConstants.otherLinks[0].url;
    component.checkUrl(); expect(component.activeNavItem).toBe(5);

    // layers
    routerMock.url = SidebarConstants.mapLinks[0].url;
    component.checkUrl(); expect(component.activeNavItem).toBe(6);

    // legend
    routerMock.url = SidebarConstants.mapLinks[1].url;
    component.checkUrl(); expect(component.activeNavItem).toBe(7);

    // graph
    routerMock.url = SidebarConstants.mapLinks[2].url;
    component.checkUrl(); expect(component.activeNavItem).toBe(8);

    // satellite
    routerMock.url = SidebarConstants.geosLinks[0].url;
    component.checkUrl();
    expect(component.activeNavItem).toBe(9);
    expect(component.isGeoMenuOpen).toBeTrue;

    // raster
    routerMock.url = SidebarConstants.geosLinks[1].url;
    component.checkUrl();
    expect(component.activeNavItem).toBe(10);
    expect(component.isGeoMenuOpen).toBeTrue;

    // vetorial
    routerMock.url = SidebarConstants.geosLinks[2].url;
    component.checkUrl();
    expect(component.activeNavItem).toBe(11);
    expect(component.isGeoMenuOpen).toBeTrue;

    // home (default)
    routerMock.url = 'admin/home';
    component.checkUrl();
    expect(component.activeNavItem).toBe(0);

    // all method calls
    expect(checkUrlSpy).toHaveBeenCalledTimes(12);

  });

  it('T25.8 should call #selectNavCategory on nav item click', () => {
    const selectNavSpy = spyOn(component, 'selectNavCategory');

    // to get all possible nav items
    component.isGeoMenuOpen = true;
    fixture.detectChanges();

    // nav elements
    let usersNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[0].nativeElement;
    let groupsNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[1].nativeElement;
    let contribsNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[2].nativeElement;
    let eventsNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[3].nativeElement;
    let realEventsNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[4].nativeElement;
    let layersNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[5].nativeElement;
    let legendNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[6].nativeElement;
    let graphNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[7].nativeElement;
    let satelliteNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[9].nativeElement;
    let rasterNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[10].nativeElement;
    let vectorialNavEl = fixture.debugElement.queryAll(By.css('.nav-item'))[11].nativeElement;

    // initial values
    expect(component.activeNavItem).toBe(0);
    expect(component.isNavCollapsed).toBeFalse;
    expect(component.isGeoMenuOpen).toBeTrue;

    // users click on open nav
    usersNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(1);
    // groups click on open nav
    groupsNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(2);
    // contribs click on open nav
    contribsNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(3);
    // events click on open nav
    eventsNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(4);
    // real events click on open nav
    realEventsNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(5);
    // layers click on open nav
    layersNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(6);
    // legend click on open nav
    legendNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(7);
    // graph click on open nav
    graphNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(8);
    // satellite click on open nav
    satelliteNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(9);
    // raster click on open nav
    rasterNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(10);
    // vectorial click on open nav
    vectorialNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(11);

    // collapse nav
    component.isNavCollapsed = true;
    fixture.detectChanges();
    expect(component.isNavCollapsed).toBeTrue;
    expect(component.isGeoMenuOpen).toBeTrue;

    // users click on closed nav
    usersNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(1);
    // groups click on closed nav
    groupsNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(2);
    // contribs click on closed nav
    contribsNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(3);
    // events click on closed nav
    eventsNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(4);
    // real events click on closed nav
    realEventsNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(5);
    // layers click on closed nav
    layersNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(6);
    // legend click on closed nav
    legendNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(7);
    // graph click on closed nav
    graphNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(8);
    // satellite click on closed nav
    satelliteNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(9);
    // raster click on closed nav
    rasterNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(10);
    // vectorial click on closed nav
    vectorialNavEl.click(); expect(selectNavSpy).toHaveBeenCalledWith(11);
  });

  it('T25.9 should correctly select category', fakeAsync(() => {
    // spies
    const selectCategorySpy = spyOn(component, 'selectNavCategory').and.callThrough();
    const itemEmitterSpy = spyOn(component.activeNavItemEmitter, 'emit').and.callThrough();
    //const routerSpy = spyOn(component['router'], 'navigate').and.callThrough();

    // initial value
    expect(component.activeNavItem).toBe(0);

    // users
    component.selectNavCategory(1);
    expect(component.activeNavItem).toBe(1);
    expect(itemEmitterSpy).toHaveBeenCalledWith(1);
    tick();
    fixture.detectChanges();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.usersLinks[0].url]);

    // groups
    component.selectNavCategory(2);
    expect(component.activeNavItem).toBe(2);
    expect(itemEmitterSpy).toHaveBeenCalledWith(2);
    tick();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.usersLinks[1].url]);

    // contributions
    component.selectNavCategory(3);
    expect(component.activeNavItem).toBe(3);
    expect(itemEmitterSpy).toHaveBeenCalledWith(3);
    tick();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.contribLinks[0].url]);

    // events
    component.selectNavCategory(4);
    expect(component.activeNavItem).toBe(4);
    expect(itemEmitterSpy).toHaveBeenCalledWith(4);
    tick();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.contribLinks[1].url]);

    // real events
    component.selectNavCategory(5);
    expect(component.activeNavItem).toBe(5);
    expect(itemEmitterSpy).toHaveBeenCalledWith(5);
    tick();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.otherLinks[0].url]);

    // layers
    component.selectNavCategory(6);
    expect(component.activeNavItem).toBe(6);
    expect(itemEmitterSpy).toHaveBeenCalledWith(6);
    tick();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.mapLinks[0].url]);

    // legend
    component.selectNavCategory(7);
    expect(component.activeNavItem).toBe(7);
    expect(itemEmitterSpy).toHaveBeenCalledWith(7);
    tick();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.mapLinks[1].url]);

    // graphs
    component.selectNavCategory(8);
    expect(component.activeNavItem).toBe(8);
    expect(itemEmitterSpy).toHaveBeenCalledWith(8);
    tick();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.mapLinks[2].url]);

    // satellite
    component.selectNavCategory(9);
    expect(component.activeNavItem).toBe(9);
    expect(itemEmitterSpy).toHaveBeenCalledWith(9);
    tick();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.geosLinks[0].url]);

    // raster
    component.selectNavCategory(10);
    expect(component.activeNavItem).toBe(10);
    expect(itemEmitterSpy).toHaveBeenCalledWith(10);
    tick();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.geosLinks[1].url]);

    // vetorial
    component.selectNavCategory(11);
    expect(component.activeNavItem).toBe(11);
    expect(itemEmitterSpy).toHaveBeenCalledWith(11);
    tick();
    expect(routerMock.navigate).toHaveBeenCalledWith([SidebarConstants.geosLinks[2].url]);

    // home (default)
    component.selectNavCategory(0);
    expect(component.activeNavItem).toBe(0);
    expect(itemEmitterSpy).toHaveBeenCalledWith(0);

    // all method calls
    expect(selectCategorySpy).toHaveBeenCalledTimes(12);

  }));

  it('T25.10 should get user name', () => {
    // spies
    let getUserSpy = spyOn(component['userServ'], 'getUser')
      .and.returnValue(of({ first_name: 'Name', last_name: 'Surname' }));
    let getNameSpy = spyOn(component, 'getUserName').and.callThrough();

    component.getUserName();

    // expectations
    expect(getNameSpy).toHaveBeenCalled();
    expect(getUserSpy).toHaveBeenCalled();
    expect(component.userName).toEqual('Name Surname');
  });

  it('T25.11 should handle error getting user name', () => {
    // spies
    let getUserSpy = spyOn(component['userServ'], 'getUser')
      .and.returnValue(throwError(() => new Error()));
    let getNameSpy = spyOn(component, 'getUserName').and.callThrough();

    component.getUserName();

    // expectations
    expect(getNameSpy).toHaveBeenCalled();
    expect(getUserSpy).toHaveBeenCalled();
    expect(component.userName).toEqual('');
  });

  it('T25.12 should logout the user', () => {
    // spies
    let logoutServSpy = spyOn(component['authServ'], 'logout')
    let logoutSpy = spyOn(component, 'logout').and.callThrough();

    component.logout();

    // expectations
    expect(logoutSpy).toHaveBeenCalled();
    expect(logoutServSpy).toHaveBeenCalled();
  });
});
