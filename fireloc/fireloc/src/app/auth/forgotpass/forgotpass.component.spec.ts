import { of, throwError } from 'rxjs';

// Modules
import { CommonModule } from '@angular/common';
import { AuthModule } from '../auth.module';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';

// Testing
import { ComponentFixture, TestBed } from '@angular/core/testing';

// Bootstrap
import { NgbActiveModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';

// Components
import { ForgotpassComponent } from './forgotpass.component';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';
import { HttpClientTestingModule } from '@angular/common/http/testing';

// Mock Success Result
const authResult = {
  status: {
    code: 'UNK',
    message: 'Password token was sended'
  }
}

// Mock API Error
class APIError extends Error {
  error: any;
  constructor(message: string) {
    super(message);
    this.error = { status: { message: message } }
  }
}

// Mock Auth Service
class MockAuthService {
  resetPassword(email: string) {
    return of(authResult);
  }
}

describe('TS3 ForgotpassComponent', () => {
  let component: ForgotpassComponent;
  let fixture: ComponentFixture<ForgotpassComponent>;

  // dependencies
  let modal: NgbActiveModal;

  // mock services
  let authService: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ForgotpassComponent],
      imports: [
        CommonModule,
        AuthModule,
        ReactiveFormsModule,
        FormsModule,
        NgbModule,
        HttpClientTestingModule,
        TranslateModule.forRoot({
          loader: {
            provide: TranslateLoader,
            useFactory: httpTranslateLoader,
            deps: [HttpClient]
          }
        }),
      ],
      providers: [
        { provide: AuthService, useClass: MockAuthService },
        NgbActiveModal,
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ForgotpassComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    // service
    authService = TestBed.inject(AuthService);

    // bootstrap modal
    modal = TestBed.inject(NgbActiveModal);

    // run the onInit Angular Lifecycle Method
    component.ngOnInit();
  });

  afterEach(() => { modal.close(); fixture.destroy(); });

  it('T3.1 should create', () => {
    expect(component).toBeTruthy();
  });

  // test form validity when empty
  it('T3.2 should have form invalid when empty', () => {
    expect(component.resetForm.valid).toBeFalsy();
  });

  // test email field validity
  it('T3.3 should check email field validity', () => {
    // empty email should be invalid
    let email = component.resetForm.controls['email'];
    expect(email.valid).toBeFalsy();

    // empty email should have a required error
    let errors = email.errors || {};
    expect(errors['required']).toBeTruthy();

    // non-email input should have email pattern error
    email.setValue("raquel");
    errors = email.errors || {};
    expect(errors['email']).toBeTruthy();

    // 255 character email should have maxLength error
    email.setValue("abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcab@gmail.com");
    errors = email.errors || {};
    expect(errors['maxlength']).toBeTruthy();

    // valid email should be valid
    email.setValue("raquel@gmail.com");
    errors = email.errors || {};
    expect(errors['required']).toBeFalsy();
    expect(errors['email']).toBeFalsy();
    expect(errors['maxlength']).toBeFalsy();
    expect(email.valid).toBeTruthy();
  });

  it('T3.4 should check if form has email property', () => {
    // change form to test (coverage purposes only)
    component.resetForm = new FormGroup({ fakeEmail: new FormControl(component.emailValue, []) });
    fixture.detectChanges();

    component.onSubmit();
    expect(component.emailValue).toBeUndefined();
  });

  // test form submit
  it('T3.5 should submit reset password form', () => {
    const resetPasswordSpy = spyOn(component, 'resetPassword').and.callFake(new MockAuthService().resetPassword);

    // empty form is invalid
    expect(component.resetForm.valid).toBeFalsy();

    // define valid email
    component.resetForm.controls['email'].setValue("raquel@gmail.com");

    // valid form is valid
    expect(component.resetForm.valid).toBeTruthy();

    // submit reset password form
    component.onSubmit();

    // variables' values are the expected values
    expect(component.submitted).toBeTruthy();
    expect(component.emailValue).toEqual("raquel@gmail.com");

    // should call reset password method
    expect(resetPasswordSpy).toHaveBeenCalled();
  });

  // test invalid form submission
  it('T3.6 should not submit invalid form', () => {
    const resetPasswordSpy = spyOn(component, 'resetPassword').and.callFake(new MockAuthService().resetPassword);

    // empty form is invalid
    expect(component.resetForm.valid).toBeFalsy();

    // submit reset password form
    component.onSubmit();

    // variables' values are the expected values
    expect(component.submitted).toBeFalsy();
    expect(component.emailValue).toEqual('');

    // should not call reset password method
    expect(resetPasswordSpy).not.toHaveBeenCalled();

  });

  // test reset password method
  it('T3.7 should send reset password email when attributes are received', () => {
    const modalSpy = spyOn(component.modal, 'close').and.callThrough();

    component.resetPassword("email");

    // should close the reset password modal
    expect(modalSpy).toHaveBeenCalled();
  });

  // test reset password method error
  it('T3.8 should handle reset password failure', () => {
    const resetPasswordSpy = spyOn(authService, 'resetPassword').and.returnValue(throwError(new APIError('A003')));

    // empty form is invalid
    expect(component.resetForm.valid).toBeFalsy();

    // define valid email and password
    component.resetForm.controls['email'].setValue("raquel@gmail.com");

    // valid form is valid
    expect(component.resetForm.valid).toBeTruthy();

    // submit reset password form
    component.onSubmit();

    // variables' values are the expected values
    expect(component.submitted).toBeTruthy();
    expect(component.resetForm.get('email')).toBeDefined();
    expect(component.emailValue).toEqual("raquel@gmail.com");

    // should call reset password method
    expect(resetPasswordSpy).toHaveBeenCalled();

  });

});
