import { TestBed } from '@angular/core/testing';

import { LyrextentService } from './lyrextent.service';

describe('LyrextentService', () => {
  let service: LyrextentService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LyrextentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
