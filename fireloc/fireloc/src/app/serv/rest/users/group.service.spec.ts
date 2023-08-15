import { HttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { GroupService } from './group.service';

describe('TS77 GroupService', () => {
  let service: GroupService;

  // dependencies
  let httpClientSpy: jasmine.SpyObj<HttpClient> = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put', 'delete']);

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        GroupService,
        { provide: HttpClient, useValue: httpClientSpy }
      ]
    });

    // setup
    service = TestBed.inject(GroupService);
  });

  it('T77.1 should be created', () => {
    expect(service).toBeTruthy();
  });

  it('T77.2 should send a GET request to receive groups', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getGroups(true, false).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T77.3 should send a POST request to create a new group', (done) => {
    const expectedResponse = {};

    httpClientSpy.post.and.returnValue(of(expectedResponse));
    service.addGroup('name').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T77.4 should send a PUT request to update an existing group', (done) => {
    const expectedResponse = {};

    httpClientSpy.put.and.returnValue(of(expectedResponse));
    service.updateGroup('oldName', 'newName').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T77.5 should send a DELETE request to delete an existing group', (done) => {
    const expectedResponse = {};

    httpClientSpy.delete.and.returnValue(of(expectedResponse));
    service.deleteGroup('name').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

});
