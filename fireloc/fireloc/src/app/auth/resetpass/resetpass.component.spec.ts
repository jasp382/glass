// Testing
import { NgReduxTestingModule } from '@angular-redux/store/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';

// Modules
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FeatModule } from 'src/app/feat/feat.module';

// Constants
import { routes } from 'src/app/app-routing.module';

// Redux
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';

// Component
import { ResetpassComponent } from './resetpass.component';

// Other
import { of, throwError } from 'rxjs';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';

describe('TS7 ResetpassComponent', () => {
  let component: ResetpassComponent;
  let fixture: ComponentFixture<ResetpassComponent>;

  // dependencies
  let modal: NgbActiveModal;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ResetpassComponent],
      imports: [
        HttpClientTestingModule,
        RouterTestingModule.withRoutes(routes),
        NgReduxTestingModule,
        FeatModule,
        FormsModule,
        ReactiveFormsModule,
        TranslateModule.forRoot({
          loader: {
            provide: TranslateLoader,
            useFactory: httpTranslateLoader,
            deps: [HttpClient]
          }
        }),
      ],
      providers: [
        NgbActiveModal,
        ContributionActions,
        EventActions,
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ResetpassComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    // bootstrap modal
    modal = TestBed.inject(NgbActiveModal);
  });

  afterEach(() => { modal.close(); fixture.destroy(); });

  it('T7.1 should create', () => {
    expect(component).toBeTruthy();
  });

  it('T7.2 should have password validator checking if form group properties are valid', () => {
    let validatorSpy = spyOn(component, 'passwordsValidator').and.callThrough();
    let result = component.passwordsValidator(new FormGroup({}));

    expect(validatorSpy).toHaveBeenCalled();
    expect(result).toBeNull();
  });

  it('T7.3 should have password validator returning form error if passwords don\'t match', () => {
    let validatorSpy = spyOn(component, 'passwordsValidator').and.callThrough();
    let result = component.passwordsValidator(new FormGroup({
      password: new FormControl('pass'),
      passwordConfirmation: new FormControl('password')
    }));

    expect(validatorSpy).toHaveBeenCalled();
    expect(result).toEqual({ notSame: true });
  });

  it('T7.4 should not submit change password if form is invalid', () => {
    // spies and call
    let submitSpy = spyOn(component, 'onSubmit').and.callThrough();
    let changePassSpy = spyOn(component, 'changePassword');

    component.onSubmit();

    // expectations
    expect(submitSpy).toHaveBeenCalledOnceWith();
    expect(changePassSpy).not.toHaveBeenCalled();
  });

  it('T7.5 should submit change password form', () => {
    // spies and call
    let submitSpy = spyOn(component, 'onSubmit').and.callThrough();
    let changePassSpy = spyOn(component, 'changePassword');
    component.newPasswordForm.patchValue({password: 'pass', passwordConfirmation: 'pass'});

    component.onSubmit();

    // expectations
    expect(submitSpy).toHaveBeenCalledOnceWith();
    expect(component.submitted).toBeTrue();
    expect(component.passwordValue).toBe('pass');
    expect(component.confirmationValue).toBe('pass');
    expect(changePassSpy).toHaveBeenCalledOnceWith(component.token, component.passwordValue);
  });

  it('T7.6 should check if form properties are valid', () => {
    // fake data and spy
    component.newPasswordForm = new FormGroup({});
    fixture.detectChanges();
    let submitSpy = spyOn(component, 'onSubmit').and.callThrough();

    // call
    component.onSubmit();

    // expectations
    expect(submitSpy).toHaveBeenCalledOnceWith();
    expect(component.submitted).toBeTrue();
    expect(component.passwordValue).toBeUndefined();
    expect(component.confirmationValue).toBeUndefined();

  });

  it('T7.7 should change password with auth service', () => {
    // spies
    let modalSpy = spyOn(modal, 'close');
    let authServSpy = spyOn(component['authServ'], 'changePassword')
      .and.returnValue(of({
        status: {
          code: 'S22',
          message: 'User password was changed'
        }
      }));

    // call method
    component.changePassword('', '');

    // expectations
    expect(authServSpy).toHaveBeenCalledOnceWith('', '');
    expect(modalSpy).toHaveBeenCalledOnceWith();
  });

  it('T7.8 should handle error from auth service', () => {
    // spies
    let modalSpy = spyOn(modal, 'close');
    let authServSpy = spyOn(component['authServ'], 'changePassword')
      .and.returnValue(throwError({
        error: { status: { code: 'code', message: 'msg' } }
      }));

    // call method
    component.changePassword('', '');

    // expectations
    expect(authServSpy).toHaveBeenCalledOnceWith('', '');
    expect(modalSpy).not.toHaveBeenCalled();
  });
});
