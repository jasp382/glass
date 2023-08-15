import { Component, OnInit } from '@angular/core';

// NGRX
import { AppState } from '../../stores/app-state';
import { Store } from '@ngrx/store';

import * as langSelector from '../../stores/lang/lang.reducer';
import { Language } from 'src/app/interfaces/language';

@Component({
  selector: 'app-unauthorized',
  templateUrl: './unauthorized.component.html',
  styleUrls: ['./unauthorized.component.css']
})
export class UnauthorizedComponent implements OnInit {

  constructor(
    private store: Store<AppState>
  ) { }

  /**
   * current app language
   */
  language: string = 'pt';

  ngOnInit(): void {
    this.store
      .select(langSelector.getLang)
      .subscribe((lang: Language) => {
        this.language = lang.country;
      });
  }

}
