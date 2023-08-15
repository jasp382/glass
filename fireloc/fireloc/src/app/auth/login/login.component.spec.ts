import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { routes } from 'src/app/app-routing.module';

// Modules
import { FeatModule } from 'src/app/feat/feat.module';
import { CommonModule } from '@angular/common';
import { AuthModule } from '../auth.module';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';

// Testing
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { NgReduxTestingModule, MockNgRedux } from '@angular-redux/store/testing';

// Bootstrap
import { NgbActiveModal, NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Services
import { AuthService } from 'src/app/serv/rest/users/auth.service';

// Components
import { LoginComponent } from './login.component';

// Redux
import { UserActions } from 'src/app/redux/actions/userActions';
import { AlertActions } from 'src/app/redux/actions/alertActions';

// Translate
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';

// Mock Success Result
const authResult = {
  access_token: "token",
  refresh_token: "refreshToken",
  token_type: "typeToken",
  expires_in: "expiration",
  role: "role"
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
  login(email: string, password: string) {
    return of(authResult);
  }
  setRememberUser(remember: boolean) { }

}

describe('TS6 LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;

  // dependencies
  let router: Router;
  let modalService: NgbModal;
  let modal: NgbActiveModal;
  let userActions: UserActions;

  // mock services
  let authService: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        LoginComponent,
      ],
      imports: [
        CommonModule,
        AuthModule,
        RouterTestingModule.withRoutes(routes),
        FeatModule,
        ReactiveFormsModule,
        FormsModule,
        NgbModule,
        NgReduxTestingModule,
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
        NgbModal,
        UserActions,
        AlertActions,
      ]
    }).compileComponents();

    // reset redux
    MockNgRedux.reset();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    // router
    router = TestBed.inject(Router);

    // service
    authService = TestBed.inject(AuthService);

    // bootstrap modal
    modal = TestBed.inject(NgbActiveModal);
    modalService = TestBed.inject(NgbModal);

    // run the onInit Angular Lifecycle Method
    component.ngOnInit();
  });

  afterEach(() => { modal.close(); modalService.dismissAll(); fixture.destroy(); });

  it('T6.1 should create', () => {
    expect(component).toBeTruthy();
  });

  // test form validity when empty
  it('T6.2 should have form invalid when empty', () => {
    expect(component.loginForm.valid).toBeFalsy();
  });

  it('T6.3 should check if form has email and password controls', () => {
    // change form to test (coverage purposes only)
    component.loginForm = new FormGroup({ fakeEmail: new FormControl(component.emailValue, []) });
    fixture.detectChanges();

    component.onSubmit();
    expect(component.emailValue).toBeUndefined();
    expect(component.passwordValue).toBeUndefined();
  });

  // test email field validity
  it('T6.4 should check email field validity', () => {
    // empty email should be invalid
    let email = component.loginForm.controls['email'];
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

  // test password field validity
  it('T6.5 should check password field validity', () => {
    // empty password should be invalid
    let password = component.loginForm.controls['password'];
    expect(password.valid).toBeFalsy();

    // empty password should have a required error
    let errors = password.errors || {};
    expect(errors['required']).toBeTruthy();

    // valid password should be valid
    password.setValue("raquel123");
    errors = password.errors || {};
    expect(errors['required']).toBeFalsy();
    expect(password.valid).toBeTruthy();
  });

  // test form submit
  it('T6.6 should submit login form', () => {
    const loginSpy = spyOn(component, 'logIn').and.callFake(new MockAuthService().login);

    // empty form is invalid
    expect(component.loginForm.valid).toBeFalsy();

    // define valid email and password
    component.loginForm.controls['email'].setValue("raquel@gmail.com");
    component.loginForm.controls['password'].setValue("123456789");

    // valid form is valid
    expect(component.loginForm.valid).toBeTruthy();

    // submit login form
    component.onSubmit();

    // variables' values are the expected values
    expect(component.submitted).toBeTruthy();
    expect(component.emailValue).toEqual("raquel@gmail.com");
    expect(component.passwordValue).toEqual("123456789");

    // should call login method
    expect(loginSpy).toHaveBeenCalled();
  });

  // test invalid form submission
  it('T6.7 should not submit invalid form', () => {
    const loginSpy = spyOn(component, 'logIn').and.callFake(new MockAuthService().login);

    // empty form is invalid
    expect(component.loginForm.valid).toBeFalsy();

    // submit login form
    component.onSubmit();

    // variables' values are the expected values
    expect(component.submitted).toBeFalsy();
    expect(component.emailValue).toEqual('');
    expect(component.passwordValue).toEqual('');

    // should not call login method
    expect(loginSpy).not.toHaveBeenCalled();

  });

  // test login method
  it('T6.8 should login user when attributes are received', () => {
    spyOn(Date, 'now').and.returnValue(1);
    let redirectSpy = spyOn(component, 'redirect');
    component.loginForm.controls['rememberSession'].setValue(true);

    component.logIn("email", "password");

    expect(redirectSpy).toHaveBeenCalled();
  });

  it('T6.9 should check if form has rememberSession control', () => {
    spyOn(Date, 'now').and.returnValue(1);
    let redirectSpy = spyOn(component, 'redirect');

    // change form to test (coverage purposes only)
    component.loginForm = new FormGroup({ fakeEmail: new FormControl(component.emailValue, []) });
    fixture.detectChanges();

    component.logIn("email", "password");
    expect(redirectSpy).toHaveBeenCalled();
  });

  // test login method error
  it('T6.10 should handle login failure', () => {
    const loginSpy = spyOn(authService, 'login').and.returnValue(throwError(new APIError('Wrong user or password')));

    // empty form is invalid
    expect(component.loginForm.valid).toBeFalsy();

    // define valid email and password
    component.loginForm.controls['email'].setValue("raquel@gmail.com");
    component.loginForm.controls['password'].setValue("123456789");

    // valid form is valid
    expect(component.loginForm.valid).toBeTruthy();

    // submit login form
    component.onSubmit();

    // variables' values are the expected values
    expect(component.submitted).toBeTruthy();
    expect(component.emailValue).toEqual("raquel@gmail.com");
    expect(component.passwordValue).toEqual("123456789");

    // should call login method
    expect(loginSpy).toHaveBeenCalled();
  });

  // test forget password method
  it('T6.11 should open forgot password modal', () => {
    const forgotPasswordSpy = spyOn(component, 'forgotPassword').and.callThrough();
    const loginModalSpy = spyOn(modal, 'close').and.callThrough();
    const forgotModalSpy = spyOn(modalService, 'open').and.callThrough();

    // click on the forgot password link
    let forgotLink = fixture.debugElement.nativeElement.querySelector('a');
    forgotLink.click();

    // on click method should be called
    expect(forgotPasswordSpy).toHaveBeenCalled();

    // login modal should be closed
    expect(loginModalSpy).toHaveBeenCalled();

    // forgot modal should be open
    expect(forgotModalSpy).toHaveBeenCalled();

  });

  // test redirect method
  it('T6.12 should correctly redirect users after login', () => {
    const loginModalSpy = spyOn(modal, 'close').and.callThrough();
    const reduxSpy = spyOn(MockNgRedux.getInstance(), 'dispatch');
    const routerSpy = spyOn(router, 'navigate').and.callThrough();

    // fireloc user role
    component.redirect('fireloc');
    expect(loginModalSpy).toHaveBeenCalled();                       // close login modal 
    expect(reduxSpy).toHaveBeenCalledWith({                         // redux action dispatch
      type: UserActions.GET_USER_INFO
    });
    expect(router.navigate).toHaveBeenCalledWith(['/admin']);   // redirect to correct path

    // superuser user role
    component.redirect('superuser');
    expect(loginModalSpy).toHaveBeenCalled();                       // close login modal 
    expect(reduxSpy).toHaveBeenCalledWith({                         // redux action dispatch
      type: UserActions.GET_USER_INFO
    });
    expect(router.navigate).toHaveBeenCalledWith(['/admin']);   // redirect to correct path

    // justauser user role
    component.redirect('justauser');
    expect(loginModalSpy).toHaveBeenCalled();                       // close login modal 
    expect(reduxSpy).toHaveBeenCalledWith({                         // redux action dispatch
      type: UserActions.GET_USER_INFO
    });
    expect(routerSpy).toHaveBeenCalledWith(['/geoportal']);         // redirect to correct path

  });

});


