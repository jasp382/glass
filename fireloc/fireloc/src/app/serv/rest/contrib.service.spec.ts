import { HttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ContribService } from './contrib.service';

describe('TS68 ContribService', () => {
  let service: ContribService;

  // dependencies
  let httpClientSpy: jasmine.SpyObj<HttpClient> = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put', 'delete']);

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ContribService,
        { provide: HttpClient, useValue: httpClientSpy }
      ]
    });
    service = TestBed.inject(ContribService);
  });

  it('T68.1 should be created', () => { expect(service).toBeTruthy(); });

  describe('TS68.1 should send a GET request to receive contributions', () => {
    it('T68.1.1 no filters', (done) => {
      const expectedResponse = {};
      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getContributions().subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });

    it('T68.1.2 user filter', (done) => {
      const expectedResponse = {};
      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getContributions('user').subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });

    it('T68.1.3 start date filter', (done) => {
      const expectedResponse = {};
      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getContributions('user', 'start').subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });

    it('T68.1.4 end date filter', (done) => {
      const expectedResponse = {};
      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getContributions('user', 'start', 'end').subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });

    it('T68.1.5 geographic location filter', (done) => {
      const expectedResponse = {};
      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getContributions('user', 'start', 'end', 'geom').subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });
  });

  it('T68.2 should send a GET request to receive contribution photo', (done) => {
    const expectedResponse = {};
    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getContributionPhoto('photo').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });
});
