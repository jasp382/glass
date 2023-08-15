import { HttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { SatelliteService } from './satellite.service';

describe('TS73 SatelliteService', () => {
  let service: SatelliteService;

  // dependencies
  let httpClientSpy: jasmine.SpyObj<HttpClient> = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put', 'delete']);

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        SatelliteService,
        { provide: HttpClient, useValue: httpClientSpy }
      ]
    });

    // setup
    service = TestBed.inject(SatelliteService);
  });

  it('T73.1 should be created', () => {
    expect(service).toBeTruthy();
  });

  it('T73.2 should send a GET request to receive satellite datasets', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getSatDatasets().subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T73.3 should send a DELETE request to delete an existing satellite dataset', (done) => {
    const expectedResponse = {};

    httpClientSpy.delete.and.returnValue(of(expectedResponse));
    service.deleteSatDataset('id').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });
});
