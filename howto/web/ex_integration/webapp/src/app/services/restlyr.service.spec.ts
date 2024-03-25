import { TestBed } from '@angular/core/testing';

import { RestlyrService } from './restlyr.service';

describe('RestlyrService', () => {
  let service: RestlyrService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RestlyrService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
