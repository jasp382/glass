import { TestBed } from '@angular/core/testing';

import { LyrsService } from './lyrs.service';

describe('LyrsService', () => {
  let service: LyrsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LyrsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
