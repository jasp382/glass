import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { FeatModule } from 'src/app/feat/feat.module';

// Redux
import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';
import { LangActions } from 'src/app/redux/actions/langActions';

// Component
import { UnauthorizedComponent } from './unauthorized.component';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';
import { selectLanguage } from 'src/app/redux/selectors';

describe('TS9 UnauthorizedComponent', () => {
  let component: UnauthorizedComponent;
  let fixture: ComponentFixture<UnauthorizedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [UnauthorizedComponent],
      imports: [
        FeatModule,
        HttpClientTestingModule,
        RouterTestingModule,
        NgReduxTestingModule,
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

    // reset redux
    MockNgRedux.reset();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UnauthorizedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T9.1 should create', () => { expect(component).toBeTruthy(); });

  it('T9.2 should update language from redux', () => {
    // spies
    let reduxSubSpy = spyOn(component, 'subscribeToRedux').and.callThrough();

    // select language state and initialize
    const langStub = MockNgRedux.getSelectorStub(selectLanguage);
    langStub.next('pt');
    langStub.complete();

    component.subscribeToRedux();

    // expectations
    expect(reduxSubSpy).toHaveBeenCalledOnceWith();
    component.language$.subscribe(
      (actualInfo: any) => {
        // alert received should be as expected        
        expect(actualInfo).toEqual('pt');
        expect(component.language).toEqual('pt');
      }
    );
  });
});
