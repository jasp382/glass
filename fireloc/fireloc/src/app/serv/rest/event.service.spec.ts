import { HttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { EventService } from './event.service';

describe('TS69 EventService', () => {
  let service: EventService;

  // dependencies
  let httpClientSpy: jasmine.SpyObj<HttpClient> = jasmine.createSpyObj('HttpClient', ['get']);


  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        EventService,
        { provide: HttpClient, useValue: httpClientSpy }
      ]
    });
    service = TestBed.inject(EventService);
  });

  it('T69.1 should be created', () => { expect(service).toBeTruthy(); });

  it('T69.2 should send a GET request to receive fireloc events (no authentication)', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getEventsNoToken().subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T69.3 should send a GET request to receive fireloc events (authentication)', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getEventsToken().subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });
});
