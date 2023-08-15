import { TestBed } from '@angular/core/testing';

import { GeosrvService } from './geosrv.service';

describe('GeosrvService', () => {
  let service: GeosrvService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GeosrvService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
