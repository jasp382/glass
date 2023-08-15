import { TestBed } from '@angular/core/testing';

import { FlocsService } from './flocs.service';

describe('FlocsService', () => {
  let service: FlocsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FlocsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
