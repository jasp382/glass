import { TestBed } from '@angular/core/testing';

import { BasemapsService } from './basemaps.service';

describe('BasemapsService', () => {
  let service: BasemapsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BasemapsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
