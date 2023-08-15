import { HttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { RasterService } from './raster.service';

describe('TS72 RasterService', () => {
  let service: RasterService;

  // dependencies
  let httpClientSpy: jasmine.SpyObj<HttpClient> = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put', 'delete']);

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        RasterService,
        { provide: HttpClient, useValue: httpClientSpy }
      ]
    });

    // setup
    service = TestBed.inject(RasterService);
  });

  it('T72.1 should be created', () => {
    expect(service).toBeTruthy();
  });

  it('T72.2 should send a GET request to receive raster datasets', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getRasterDatasets().subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T72.3 should send a GET request to receive raster dataset types', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getRasterTypes().subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T72.4 should send a POST request to add a new raster dataset', (done) => {
    const expectedResponse = {};

    httpClientSpy.post.and.returnValue(of(expectedResponse));
    service.addRasterDataset({}).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T72.5 should send a PUT request to update an existing raster dataset', (done) => {
    const expectedResponse = {};

    httpClientSpy.put.and.returnValue(of(expectedResponse));
    service.updateRasterDataset('slug', {}).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T72.6 should send a DELETE request to delete an existing raster dataset', (done) => {
    const expectedResponse = {};

    httpClientSpy.delete.and.returnValue(of(expectedResponse));
    service.deleteRasterDataset('slug').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });
});
