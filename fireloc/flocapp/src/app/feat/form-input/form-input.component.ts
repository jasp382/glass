import { Component, forwardRef, Input, OnInit } from '@angular/core';
import { AbstractControl, ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

/**
 * Form input component.
 * 
 * Displays a modular input used in the {@link LoginComponent} and {@link SignupComponent}.
 */
@Component({
  selector: 'app-form-input',
  templateUrl: './form-input.component.html',
  styleUrls: ['./form-input.component.css'],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => FormInputComponent),
      multi: true
    }
  ]
})
export class FormInputComponent implements OnInit, ControlValueAccessor {
  /**
   * input icon
   */
  @Input('icon') icon: any;
  /**
   * visible input content icon
   */
  @Input('showIcon') showIcon: any;
  /**
   * hidden input content icon
   */
  @Input('hideIcon') hideIcon: any;

  /**
   * input type (email, text, ...)
   */
  @Input('inputType') inputType: string;
  /**
   * input placeholder value
   */
  @Input('inputPlaceholder') inputPlaceholder: string;

  /**
   * password toggle to show/hide input content
   */
  showPassword = false;

  /**
   * flag to determine if input is required in the form or not
   */
  @Input('required') isRequired: boolean;
  /**
   * form control the input is integrated in
   */
  @Input() inputFormControl!: AbstractControl | null;
  /**
   * input content value
   */
  innerValue: string = '';

  /**
   * Control Value Accessor onChange
   */
  onChange: any = () => { }
  /**
   * Control Value Accessor onTouch
   */
  onTouch: any = () => { }

  /**
   * Form input constructor. 
   * Initializes default values for the input type, placeholder and required flag to garantee the values exist in the template.
   */
  constructor() {
    // default values
    this.inputType = "text";
    this.inputPlaceholder = "Placeholder";
    this.isRequired = true;
  }

  /**
   * Empty ngOnInit.
   */
  ngOnInit(): void { }

  /**
   * Show or hide password input content. 
   * Changes the type of input to 'text' to show content or to 'password' to hide it.
   * @param password HTML input elememnt to change the type
   */
  togglePassword(password: HTMLInputElement) {
    this.showPassword = !this.showPassword;
    this.showPassword ? password.type = 'text' : password.type = 'password';
  }

  // Control Value Accessor Interface implementation
  /**
   * Updates the value of the input in the component with the user's input.
   * @param input user's input in the form input
   */
  writeValue(input: string): void { this.innerValue = input; }
  /**
   * Registers a method to be called on input changed.
   * @param fn method to be called
   */
  registerOnChange(fn: any): void { this.onChange = fn; }
  /**
   * Registers a method to be called on input touch.
   * @param fn method to be called
   */
  registerOnTouched(fn: any): void { this.onTouch = fn; }
}
