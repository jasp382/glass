import { FormControl } from '@angular/forms';
import { By } from '@angular/platform-browser';

// Testing
import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';

// Modules
import { FeatModule } from '../feat.module';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

import { faEnvelope } from '@fortawesome/free-solid-svg-icons';

// Components
import { FormInputComponent } from './form-input.component';

describe('TS27 FormInputComponent', () => {
  let component: FormInputComponent;
  let fixture: ComponentFixture<FormInputComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [FormInputComponent],
      imports: [
        FeatModule,
        FontAwesomeModule,
      ]
    }).compileComponents();

    // component for testing
    fixture = TestBed.createComponent(FormInputComponent);
    component = fixture.componentInstance;

    // default dummy data for inputs
    component.icon = faEnvelope;
    component.showIcon = faEnvelope;
    component.hideIcon = faEnvelope;
    component.inputType = 'string';
    component.inputPlaceholder = 'email';
    component.isRequired = true;
    component.inputFormControl = new FormControl();

    // trigger initial data binding
    fixture.detectChanges();

    // run the onInit Angular Lifecycle Method
    component.ngOnInit();
  });

  it('T27.1 should create', () => {
    expect(component).toBeTruthy();
  });

  it('T27.2 should have defaults for onChange and onTouch', () => {
    // spies
    let changeSpy = jasmine.createSpy('selector', component.onChange);
    let touchSpy = jasmine.createSpy('selector', component.onTouch);
    // calls
    component.onChange();
    component.onTouch();
    // expectations
    expect(typeof changeSpy).toBe('function');
    expect(typeof touchSpy).toBe('function');
  })

  // testing toggle password
  it('T27.3 should toggle password', fakeAsync(() => {
    // change input type to password
    component.inputType = 'password';
    fixture.detectChanges();

    // toggle spy
    const togglePasswordSpy = spyOn(component, 'togglePassword').and.callThrough();

    // initial variable is false
    expect(component.showPassword).toBeFalsy();

    // get input element reference
    const element = fixture.debugElement.query(By.css('.form-control')).nativeElement;
    const clickIcon = fixture.debugElement.query(By.css('.show-symbol')).nativeElement;

    // toggle
    clickIcon.click();
    tick();

    // method should be called
    expect(togglePasswordSpy).toHaveBeenCalled();
    // show password toggle should be true
    expect(component.showPassword).toBeTruthy();
    // as password is being shown, html type should be text
    expect(element.type).toBe('text');

    // toggle again
    clickIcon.click();
    tick();

    // method should be called
    expect(togglePasswordSpy).toHaveBeenCalled();
    // show password toggle should be true
    expect(component.showPassword).toBeFalsy();
    // as password is being shown, html type should be text
    expect(element.type).toBe('password');

  }));

  // testing write value
  it('T27.4 write value shoud change inner value', () => {
    const writeValueSpy = spyOn(component, 'writeValue').and.callThrough();

    // initial variable data is empty
    expect(component.innerValue).toBe('');

    // get test data and writeValue
    const data = 'Hello input value';
    component.writeValue(data);

    // method should be called
    expect(writeValueSpy).toHaveBeenCalled();
    // inner value should be dummy data provided
    expect(component.innerValue).toBe(data);
  });

  // testing register on change
  it('T27.5 registerOnChange should define onChange method', () => {
    const registerOnChangeSpy = spyOn(component, 'registerOnChange').and.callThrough();

    // initial variable method is empty function
    let initialFun = jasmine.any(Function);
    expect(component.onChange).toEqual(initialFun);

    // prepare test data and call method
    let testFun = (a: string, b: string) => { return a + b };
    component.registerOnChange(testFun);

    // method should be called
    expect(registerOnChangeSpy).toHaveBeenCalled();
    // onChange should be the test data function
    expect(component.onChange).toEqual(testFun);
  });

  // testing register on touched
  it('T27.6 registerOnTouched should define onTouch method', () => {
    const registerOnTouchedSpy = spyOn(component, 'registerOnTouched').and.callThrough();

    // initial variable method is empty function
    let initialFun = jasmine.any(Function);
    expect(component.onTouch).toEqual(initialFun);

    // prepare test data and call method
    let testFun = (a: string, b: string) => { return a + b };
    component.registerOnTouched(testFun);

    // method should be called
    expect(registerOnTouchedSpy).toHaveBeenCalled();
    // onTouch should be the test data function
    expect(component.onTouch).toEqual(testFun);
  });
});
