import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Testing
import { NgReduxTestingModule } from '@angular-redux/store/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';

// Redux
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';
import { LayerActions } from 'src/app/redux/actions/layerActions';

// Components
import { LeftcontrolComponent } from './leftcontrol.component';
import { LayersbarComponent } from '../layersbar/layersbar.component';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';

describe('TS38 LeftcontrolComponent', () => {
  let component: LeftcontrolComponent;
  let fixture: ComponentFixture<LeftcontrolComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LeftcontrolComponent, LayersbarComponent],
      imports: [
        NgbModule,
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
        LayerActions
      ]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LeftcontrolComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T38.1 should create', () => { expect(component).toBeTruthy(); });
});
