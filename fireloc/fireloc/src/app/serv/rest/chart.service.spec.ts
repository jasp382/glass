import { HttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ChartService } from './chart.service';

describe('TS67 ChartService', () => {
  let service: ChartService;

  // dependencies
  let httpClientSpy: jasmine.SpyObj<HttpClient> = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put', 'delete']);

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ChartService,
        { provide: HttpClient, useValue: httpClientSpy }
      ]
    });

    // setup
    service = TestBed.inject(ChartService);
  });

  it('T67.1 should be created', () => {
    expect(service).toBeTruthy();
  });

  it('T67.2 should send a GET request to receive geocharts', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getCharts().subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T67.3 should send a POST request to add a new geochart', (done) => {
    const expectedResponse = {};

    httpClientSpy.post.and.returnValue(of(expectedResponse));
    service.addChart({}).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T67.4 should send a PUT request to update an existing geochart', (done) => {
    const expectedResponse = {};

    httpClientSpy.put.and.returnValue(of(expectedResponse));
    service.updateChart('slug', {}).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T67.5 should send a DELETE request to delete an existing geochart', (done) => {
    const expectedResponse = {};

    httpClientSpy.delete.and.returnValue(of(expectedResponse));
    service.deleteChart('slug').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });
});
