import { NgReduxTestingModule } from '@angular-redux/store/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';
import { LeafmapComponent } from 'src/app/feat/leafmap/leafmap.component';
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';
import { MarkerService } from 'src/app/serv/leafmap/marker.service';
import { AuthService } from 'src/app/serv/rest/users/auth.service';
import { GroupService } from 'src/app/serv/rest/users/group.service';
import { UserService } from 'src/app/serv/rest/users/user.service';

import { DashboardComponent } from './dashboard.component';

describe('TS12 Backoffice DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DashboardComponent, LeafmapComponent],
      schemas: [NO_ERRORS_SCHEMA],
      imports: [
        HttpClientTestingModule,
        RouterTestingModule,
        NgReduxTestingModule,
      ],
      providers: [
        AuthService,
        MarkerService,
        UserService,
        GroupService,
        ContributionActions,
        EventActions,
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach(function () {
    jasmine.clock().uninstall();
  });

  it('T12.1 should create', () => { expect(component).toBeTruthy(); });

  it('T12.2 should call methods #onInit to initialize information', () => {
    let timeSpy = spyOn(component, 'getTimeGreeting');
    let nameSpy = spyOn(component, 'getUserName');
    let usersSpy = spyOn(component, 'getUsers');
    let groupsSpy = spyOn(component, 'getGroups');

    component.ngOnInit();

    expect(timeSpy).toHaveBeenCalled();
    expect(nameSpy).toHaveBeenCalled();
    expect(usersSpy).toHaveBeenCalled();
    expect(groupsSpy).toHaveBeenCalled();
  });

  it('T12.3 should define greeting according to local time (morning)', () => {
    jasmine.clock().install();
    var baseTime = new Date(2022, 12, 12, 7, 0, 0);
    jasmine.clock().mockDate(baseTime);

    component.getTimeGreeting();
    expect(component.timeGreeting).toEqual('Bom Dia');
  });

  it('T12.4 should define greeting according to local time (afternoon)', () => {
    jasmine.clock().install();
    var baseTime = new Date(2022, 12, 12, 13, 0, 0);
    jasmine.clock().mockDate(baseTime);

    component.getTimeGreeting();
    expect(component.timeGreeting).toEqual('Boa Tarde');
  });

  it('T12.5 should define greeting according to local time (night)', () => {
    jasmine.clock().install();
    var baseTime = new Date(2022, 12, 12, 19, 0, 0);
    jasmine.clock().mockDate(baseTime);

    component.getTimeGreeting();
    expect(component.timeGreeting).toEqual('Boa Noite');
  });

  it('T12.6 should get user name from API', () => {
    let userAPISpy = spyOn(component['userServ'], 'getUser')
      .and.returnValue(of({ first_name: 'First Name' }));

    component.getUserName();
    expect(userAPISpy).toHaveBeenCalled();
    expect(component.userName).toEqual('First Name');
  });

  it('T12.7 should handle error from getting user name from API', () => {
    let userAPISpy = spyOn(component['userServ'], 'getUser')
      .and.returnValue(throwError(() => new Error()));

    component.getUserName();
    expect(userAPISpy).toHaveBeenCalled();
    expect(component.userName).toEqual('');
  });

  it('T12.8 should get users from API', () => {
    let usersAPISpy = spyOn(component['userServ'], 'getUsers')
      .and.returnValue(of({ data: [{}, {}] }));

    component.getUsers();
    expect(usersAPISpy).toHaveBeenCalled();
    expect(component.totalUsers).toEqual('2');
  });

  it('T12.9 should handle error from getting users from API', () => {
    let usersAPISpy = spyOn(component['userServ'], 'getUsers')
      .and.returnValue(throwError(() => new Error()));

    component.getUsers();
    expect(usersAPISpy).toHaveBeenCalled();
    expect(component.totalUsers).toEqual('');
  });

  it('T12.10 should get groups from API', () => {
    let groupsAPISpy = spyOn(component['groupServ'], 'getGroups')
      .and.returnValue(of({ data: [{}, {}] }));

    component.getGroups();
    expect(groupsAPISpy).toHaveBeenCalled();
    expect(component.totalGroups).toEqual('2');
  });

  it('T12.11 should handle error from getting groups from API', () => {
    let groupsAPISpy = spyOn(component['groupServ'], 'getGroups')
      .and.returnValue(throwError(() => new Error()));

    component.getGroups();
    expect(groupsAPISpy).toHaveBeenCalled();
    expect(component.totalGroups).toEqual('');
  });

  it('T12.12 should add fire markers if map is received', () => {
    let firesSpy = spyOn(component, 'addFireMakers').and.callThrough();
    let markerSpy = spyOn(component['markerServ'], 'addCustomMarkerToMap');

    component.addFireMakers();

    expect(component.map).not.toBeNull();
    expect(firesSpy).toHaveBeenCalled();
    expect(markerSpy).toHaveBeenCalledTimes(5);
  });

  it('T12.13 should not add fire markers if map is null', () => {
    component.map = null;
    fixture.detectChanges();

    let firesSpy = spyOn(component, 'addFireMakers').and.callThrough();
    let markerSpy = spyOn(component['markerServ'], 'addCustomMarkerToMap');

    component.addFireMakers();

    expect(component.map).toBeNull();
    expect(firesSpy).toHaveBeenCalled();
    expect(markerSpy).not.toHaveBeenCalled();
  });

  it('T12.14 should logout the user', () => {
    let authSpy = spyOn(component['authServ'], 'logout');
    component.logout();
    expect(authSpy).toHaveBeenCalled();
  });
});
