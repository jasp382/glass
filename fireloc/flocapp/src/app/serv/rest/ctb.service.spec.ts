import { TestBed } from '@angular/core/testing';

import { CtbService } from './ctb.service';

describe('CtbService', () => {
  let service: CtbService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CtbService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
