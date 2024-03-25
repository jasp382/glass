import { TestBed } from '@angular/core/testing';

import { GeosService } from './geos.service';

describe('GeosService', () => {
  let service: GeosService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GeosService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
