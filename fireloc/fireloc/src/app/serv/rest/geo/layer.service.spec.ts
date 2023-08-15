import { HttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { LayerService } from './layer.service';

describe('TS71 LayerService', () => {
  let service: LayerService;

  // dependencies
  let httpClientSpy: jasmine.SpyObj<HttpClient> = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put', 'delete']);

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        LayerService,
        { provide: HttpClient, useValue: httpClientSpy }
      ]
    });

    // setup
    service = TestBed.inject(LayerService);
  });

  it('T71.1 should be created', () => {
    expect(service).toBeTruthy();
  });

  it('T71.2 should send a GET request to receive geographical layers (no access token)', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getLayersNoToken().subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T71.3 should send a GET request to receive geographical layers (access token, no tree structure)', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getLayersToken().subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T71.4 should send a GET request to receive geographical layers (access token, tree structure)', (done) => {
    const expectedResponse = {};

    httpClientSpy.get.and.returnValue(of(expectedResponse));
    service.getLayersToken(true).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T71.5 should send a POST request to add a new geographical layer', (done) => {
    const expectedResponse = {};

    httpClientSpy.post.and.returnValue(of(expectedResponse));
    service.createLayer({}).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T71.6 should send a PUT request to update an existing geographical layer', (done) => {
    const expectedResponse = {};

    httpClientSpy.put.and.returnValue(of(expectedResponse));
    service.updateLayer('slug', {}).subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T71.7 should send a DELETE request to delete an existing geographical layer', (done) => {
    const expectedResponse = {};

    httpClientSpy.delete.and.returnValue(of(expectedResponse));
    service.deleteLayer('slug').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T71.8 should send a PUT request to update layers visible to a specific group (delete layers)', (done) => {
    const expectedResponse = {};

    httpClientSpy.put.and.returnValue(of(expectedResponse));
    service.setGroupLayers('groupName', [], 'delete').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T71.9 should send a PUT request to update layers visible to a specific group (add layers)', (done) => {
    const expectedResponse = {};

    httpClientSpy.put.and.returnValue(of(expectedResponse));
    service.setGroupLayers('groupName', [], 'add').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

  it('T71.10 should send a DELETE request to delete all layers visible to a specific group', (done) => {
    const expectedResponse = {};

    httpClientSpy.delete.and.returnValue(of(expectedResponse));
    service.deleteGroupLayers('groupName').subscribe({
      next: response => {
        expect(response).toEqual(expectedResponse);
        done();
      },
      error: done.fail
    });
  });

});
