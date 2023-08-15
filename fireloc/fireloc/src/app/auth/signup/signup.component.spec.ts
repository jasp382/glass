// Testing
import { NgReduxTestingModule } from '@angular-redux/store/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

// Modules
import { FeatModule } from 'src/app/feat/feat.module';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NgbActiveModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';

// Redux
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';
import { UserActions } from 'src/app/redux/actions/userActions';

// Component
import { SignupComponent } from './signup.component';

// Other
import { routes } from 'src/app/app-routing.module';
import { of, throwError } from 'rxjs';


// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';

describe('TS8 SignupComponent', () => {
	let component: SignupComponent;
	let fixture: ComponentFixture<SignupComponent>;

	let modal: NgbActiveModal;

	beforeEach(() => {
		TestBed.configureTestingModule({
			declarations: [
				SignupComponent,
			],
			imports: [
				HttpClientTestingModule,
				RouterTestingModule.withRoutes(routes),
				NgReduxTestingModule,
				FeatModule,
				FormsModule,
				ReactiveFormsModule,
				NgbModule,
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
				UserActions,
			]
		}).compileComponents();

		fixture = TestBed.createComponent(SignupComponent);
		component = fixture.componentInstance;
		fixture.detectChanges();

		// bootstrap modal
		modal = TestBed.inject(NgbActiveModal);
	});

	afterEach(() => { modal.close(); });

	it('T8.1 should create', () => { expect(component).toBeTruthy(); });

	it('T8.2 should check if form has password properties in password validator', () => {
		// form to test (coverage purposes only)
		component.registerForm = new FormGroup({ fakePassword: new FormControl(component.passwordValue, []) });
		let validatorSpy = spyOn(component, 'passwordsValidator').and.callThrough();
		fixture.detectChanges();

		//component.onSubmit();
		let validation = component.passwordsValidator(component.registerForm);
		expect(validatorSpy).toHaveBeenCalled();
		expect(validation).toBeNull();
	});

	it('T8.3 should have password validator returning form error if passwords don\'t match', () => {
		let validatorSpy = spyOn(component, 'passwordsValidator').and.callThrough();
		let result = component.passwordsValidator(new FormGroup({
			password: new FormControl('pass'),
			passwordConfirmation: new FormControl('password')
		}));

		expect(validatorSpy).toHaveBeenCalled();
		expect(result).toEqual({ notSame: true });
	});

	it('T8.4 should check form properties on submit', () => {
		// spies and setup
		let submitSpy = spyOn(component, 'onSubmit').and.callThrough();
		let registerSpy = spyOn(component, 'registerUser');
		component.registerForm = new FormGroup({ fakePassword: new FormControl(component.passwordValue, []) });
		fixture.detectChanges();

		component.onSubmit();

		// expectations
		expect(submitSpy).toHaveBeenCalled();
		expect(component.submitted).toBeTrue();
		expect(component.nameValue).toBeUndefined();
		expect(component.lastNameValue).toBeUndefined();
		expect(component.emailValue).toBeUndefined();
		expect(component.passwordValue).toBeUndefined();
		expect(component.confirmationValue).toBeUndefined();
		expect(registerSpy).toHaveBeenCalled();
	});

	it('T8.5 should not register user if form is invalid', () => {
		// spies and setup
		let submitSpy = spyOn(component, 'onSubmit').and.callThrough();
		let registerSpy = spyOn(component, 'registerUser');
		component.registerForm.patchValue({
			email: 'email@gmail.com',
			name: 'name',
			lastName: 'lastName',
			password: 'password',
			confirmation: 'not password',
		});

		component.onSubmit();

		// expectations
		expect(submitSpy).toHaveBeenCalled();
		expect(registerSpy).not.toHaveBeenCalled();
	});

	it('T8.6 should submit form values to register user', () => {
		// spies and setup
		let submitSpy = spyOn(component, 'onSubmit').and.callThrough();
		let registerSpy = spyOn(component, 'registerUser');
		component.registerForm.patchValue({
			email: 'email@gmail.com',
			name: 'name',
			lastName: 'lastName',
			password: 'password',
			confirmation: 'password',
		});

		component.onSubmit();

		// expectations
		expect(submitSpy).toHaveBeenCalled();
		expect(component.submitted).toBeTrue();
		expect(component.nameValue).toBe('name');
		expect(component.lastNameValue).toBe('lastName');
		expect(component.emailValue).toBe('email@gmail.com');
		expect(component.passwordValue).toBe('password');
		expect(component.confirmationValue).toBe('password');
		expect(registerSpy).toHaveBeenCalled();
	});

	it('T8.7 should register user and send registration confirmation on success', () => {
		// spies
		let authRegisterSpy = spyOn(component['authServ'], 'registerUser')
			.and.returnValue(of({
				status: {
					code: 'S21',
					message: 'New user was created'
				}
			}));
		let authRegisterConfirmationSpy = spyOn(component['authServ'], 'sendRegistrationConfirmation')
			.and.returnValue(of({
				status: {
					code: 'UNK',
					message: 'User confirmation token was sended'
				}
			}));
		let registerSpy = spyOn(component, 'registerUser').and.callThrough();
		let loginSpy = spyOn(component, 'login');
		let modalSpy = spyOn(component.modal, 'close');

		// setup
		component.nameValue = 'name';
		component.lastNameValue = 'lastName';
		component.emailValue = 'email';
		component.passwordValue = 'password';
		fixture.detectChanges();

		component.registerUser();

		// expectations
		expect(registerSpy).toHaveBeenCalledOnceWith();
		expect(authRegisterSpy).toHaveBeenCalledOnceWith('name', 'lastName', 'email', 'password');
		expect(authRegisterConfirmationSpy).toHaveBeenCalledOnceWith('email');
		expect(modalSpy).toHaveBeenCalledOnceWith();
		expect(loginSpy).toHaveBeenCalledOnceWith();
	});

	it('T8.8 should handle error in user registration', () => {
		// spies
		let authRegisterSpy = spyOn(component['authServ'], 'registerUser')
			.and.returnValue(throwError({
				error: { status: { code: 'code', message: 'msg' } }
			}));
		let registerSpy = spyOn(component, 'registerUser').and.callThrough();

		// setup
		component.nameValue = 'name';
		component.lastNameValue = 'lastName';
		component.emailValue = 'email';
		component.passwordValue = 'password';
		fixture.detectChanges();

		component.registerUser();

		// expectations
		expect(registerSpy).toHaveBeenCalledOnceWith();
		expect(authRegisterSpy).toHaveBeenCalledOnceWith('name', 'lastName', 'email', 'password');
	});

	it('T8.9 should handle error in user registration confirmation', () => {
		// spies
		let authRegisterSpy = spyOn(component['authServ'], 'registerUser')
			.and.returnValue(of({
				status: {
					code: 'S21',
					message: 'New user was created'
				}
			}));
		let authRegisterConfirmationSpy = spyOn(component['authServ'], 'sendRegistrationConfirmation')
			.and.returnValue(throwError({
				error: { status: { code: 'code', message: 'msg' } }
			}));
		let registerSpy = spyOn(component, 'registerUser').and.callThrough();
		let loginSpy = spyOn(component, 'login');
		let modalSpy = spyOn(component.modal, 'close');

		// setup
		component.nameValue = 'name';
		component.lastNameValue = 'lastName';
		component.emailValue = 'email';
		component.passwordValue = 'password';
		fixture.detectChanges();

		component.registerUser();

		// expectations
		expect(registerSpy).toHaveBeenCalledOnceWith();
		expect(authRegisterSpy).toHaveBeenCalledOnceWith('name', 'lastName', 'email', 'password');
		expect(authRegisterConfirmationSpy).toHaveBeenCalledOnceWith('email');
		expect(loginSpy).toHaveBeenCalledOnceWith();
		expect(modalSpy).toHaveBeenCalledOnceWith();
	});

	it('T8.10 should login user after successful registration', () => {
		// spies
		let authLoginSpy = spyOn(component['authServ'], 'login')
			.and.returnValue(of({
				access_token: 'token',
				refresh_token: 'refresh',
				token_type: 'type',
				expires_in: 'expires',
				role: 'role',
			}));
		let loginSpy = spyOn(component, 'login').and.callThrough();
		let routerSpy = spyOn(component['router'], 'navigate');

		// setup
		component.emailValue = 'email';
		component.passwordValue = 'password';
		fixture.detectChanges();

		component.login();

		// expectations
		expect(loginSpy).toHaveBeenCalledOnceWith();
		expect(authLoginSpy).toHaveBeenCalledOnceWith('email', 'password');
		expect(routerSpy).toHaveBeenCalledOnceWith(['/geoportal']);
	});

	it('T8.11 should not login if API response is unexpected', () => {
		// spies
		let authLoginSpy = spyOn(component['authServ'], 'login')
			.and.returnValue(of({
				access_token: 'token',
				refresh_token: 'refresh',
				token_type: 'type',
				expires_in: 'expires',
			}));
		let loginSpy = spyOn(component, 'login').and.callThrough();
		let routerSpy = spyOn(component['router'], 'navigate');

		// setup
		component.emailValue = 'email';
		component.passwordValue = 'password';
		fixture.detectChanges();

		component.login();

		// expectations
		expect(loginSpy).toHaveBeenCalledOnceWith();
		expect(authLoginSpy).toHaveBeenCalledOnceWith('email', 'password');
		expect(routerSpy).not.toHaveBeenCalledOnceWith(['/geoportal']);
	});

	it('T8.12 should check if register form has rememberSession control on login', () => {
		// spies
		let authLoginSpy = spyOn(component['authServ'], 'login').and.returnValue(of({
			access_token: 'token',
			refresh_token: 'refresh',
			token_type: 'type',
			expires_in: 'expires',
			role: 'role',
		}));
		let authSetSpy = spyOn(component['authServ'], 'setRememberUser');
		let loginSpy = spyOn(component, 'login').and.callThrough();
		let routerSpy = spyOn(component['router'], 'navigate');

		// change form to test (coverage purposes only)
		component.registerForm = new FormGroup({ fakeEmail: new FormControl(component.emailValue, []) });
		component.emailValue = 'email';
		component.passwordValue = 'password';
		fixture.detectChanges();

		component.login();
		expect(loginSpy).toHaveBeenCalledOnceWith();
		expect(authLoginSpy).toHaveBeenCalledOnceWith('email', 'password');
		expect(authSetSpy).toHaveBeenCalled();
		expect(routerSpy).toHaveBeenCalled();
	});

	it('T8.13 should handle error on login', () => {
		// spies
		let authLoginSpy = spyOn(component['authServ'], 'login')
			.and.returnValue(throwError({
				error: { status: { code: 'code', message: 'msg' } }
			}));
		let loginSpy = spyOn(component, 'login').and.callThrough();
		let routerSpy = spyOn(component['router'], 'navigate');

		// setup
		component.emailValue = 'email';
		component.passwordValue = 'password';
		fixture.detectChanges();

		component.login();

		// expectations
		expect(loginSpy).toHaveBeenCalledOnceWith();
		expect(authLoginSpy).toHaveBeenCalledOnceWith('email', 'password');
		expect(routerSpy).not.toHaveBeenCalledOnceWith(['/geoportal']);
	});

});
