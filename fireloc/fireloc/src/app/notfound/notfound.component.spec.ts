import { NgReduxTestingModule } from '@angular-redux/store/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { FeatModule } from '../feat/feat.module';

// Redux
import { ContributionActions } from '../redux/actions/contributionActions';
import { EventActions } from '../redux/actions/eventActions';
import { LangActions } from '../redux/actions/langActions';

import { NotfoundComponent } from './notfound.component';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';

import player from 'lottie-web';
import { LottieModule } from 'ngx-lottie';

// Separate function as it's required by the AOT compiler.
export function playerFactory() {
  return player;
}

describe('TS44 NotfoundComponent', () => {
  let component: NotfoundComponent;
  let fixture: ComponentFixture<NotfoundComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [NotfoundComponent],
      imports: [
        FeatModule,
        HttpClientTestingModule,
        RouterTestingModule,
        NgReduxTestingModule,
        LottieModule.forRoot({ player: playerFactory }),
        TranslateModule.forRoot({
          loader: {
            provide: TranslateLoader,
            useFactory: httpTranslateLoader,
            deps: [HttpClient]
          }
        }),
      ],
      providers: [
        ContributionActions,
        EventActions,
        LangActions,
      ]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(NotfoundComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T44.1 should create', () => { expect(component).toBeTruthy(); });
});
