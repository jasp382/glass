import { HttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { RealEventService } from './real-event.service';

describe('TS75 RealEventService', () => {
  let service: RealEventService;

  // dependencies
  let httpClientSpy: jasmine.SpyObj<HttpClient> = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put', 'delete']);

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        RealEventService,
        { provide: HttpClient, useValue: httpClientSpy }
      ]
    });

    // setup
    service = TestBed.inject(RealEventService);
  });

  it('T75.1 should be created', () => { expect(service).toBeTruthy(); });

  describe('TS75.1 should send a GET request to receive real events (No authentication)', () => {
    it('T75.1.1 no filters', (done) => {
      const expectedResponse = {};

      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getRealEventsNoToken().subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });

    it('T75.1.2 start date filter', (done) => {
      const expectedResponse = {};

      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getRealEventsNoToken('start').subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });

    it('T75.1.3 end date filter', (done) => {
      const expectedResponse = {};

      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getRealEventsNoToken('start', 'end').subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });

    it('T75.1.4 geographic location filter', (done) => {
      const expectedResponse = {};

      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getRealEventsNoToken('start', 'end', 'geom').subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });
  });

  describe('TS75.2 should send a GET request to receive real events (Backoffice)', () => {
    it('T75.2.1 no filters', (done) => {
      const expectedResponse = {};

      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getRealEventsToken().subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });

    it('T75.2.2 start date filter', (done) => {
      const expectedResponse = {};

      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getRealEventsToken('start').subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });

    it('T75.2.3 end date filter', (done) => {
      const expectedResponse = {};

      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getRealEventsToken('start', 'end').subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });

    it('T75.2.4 geographic location filter', (done) => {
      const expectedResponse = {};

      httpClientSpy.get.and.returnValue(of(expectedResponse));
      service.getRealEventsToken('start', 'end', 'geom').subscribe({
        next: response => {
          expect(response).toEqual(expectedResponse);
          done();
        },
        error: done.fail
      });
    });
  });

  it('T75.2 should send a POST request to add a new real event', (done) => {
    const expectedResponse = {};

    httpClientSpy.post.and.returnValue(of(expectedResponse));
    service.addRealEvent({}).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T75.3 should send a PUT request to update an existing real event', (done) => {
    const expectedResponse = {};

    httpClientSpy.put.and.returnValue(of(expectedResponse));
    service.updateRealEvent(1, {}).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T75.4 should send a DELETE request to delete an existing real event', (done) => {
    const expectedResponse = {};

    httpClientSpy.delete.and.returnValue(of(expectedResponse));
    service.deleteRealEvent(1).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

});
