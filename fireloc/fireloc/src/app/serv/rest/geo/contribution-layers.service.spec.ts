import { HttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ContributionLayersService } from './contribution-layers.service';

describe('TS70 ContributionLayersService', () => {
  let service: ContributionLayersService;

  // dependencies
  let httpClientSpy: jasmine.SpyObj<HttpClient> = jasmine.createSpyObj('HttpClient', ['get']);

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ContributionLayersService,
        { provide: HttpClient, useValue: httpClientSpy }
      ]
    });
    // setup
    service = TestBed.inject(ContributionLayersService);
  });

  it('T70.1 should be created', () => { expect(service).toBeTruthy(); });

  it('T70.2 should send a GET request to receive contribution geographical layers', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getContribLayers().subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T70.3 should send a GET request to receive contribution web feature service (no bounding box filter)', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getWebFeatureService('', '').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T70.4 should send a GET request to receive contribution web feature service (bounding box filter)', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getWebFeatureService('', '', 'box').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });
});
