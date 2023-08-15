import { EventEmitter } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';

// Modules
import { FormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';

// Component
import { SearchComponent } from './search.component';

describe('TS24 SearchComponent', () => {
  let component: SearchComponent;
  let fixture: ComponentFixture<SearchComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SearchComponent],
      imports: [
        FontAwesomeModule,
        FormsModule,
      ]
    }).compileComponents();

    // component for testing
    fixture = TestBed.createComponent(SearchComponent);
    component = fixture.componentInstance;

    // trigger initial data binding
    fixture.detectChanges();
  });

  it('T24.1 should create', () => {
    expect(component).toBeTruthy();
  });

  // testing inputs
  it('T24.2 should have correct initial values', () => {
    expect(component.placeholder).toBe('Pesquisar...');
    expect(component.searchWidth).toBe('360px');
    expect(component.searchTerms).toBe('');
    expect(component.searchIcon).toBe(faSearch);
    expect(component.searchEmitter).toEqual(new EventEmitter<string>());
  });

  it('T24.3 should have correct placeholder input', () => {
    component.placeholder = 'placeholder1';
    fixture.detectChanges();
    expect(component.placeholder).toBe('placeholder1');

    component.placeholder = 'placeholder2';
    fixture.detectChanges();
    expect(component.placeholder).toBe('placeholder2');
  });

  it('T24.4 should have correct width input', () => {
    component.searchWidth = '200px';
    fixture.detectChanges();
    expect(component.searchWidth).toBe('200px');

    component.searchWidth = '100px';
    fixture.detectChanges();
    expect(component.searchWidth).toBe('100px');
  });

  // testing emit search terms while typing
  it('T24.5 should emit value', () => {
    // setup spies
    const updateTermsSpy = spyOn(component, 'searchTyping').and.callThrough();
    const pageEmitterSpy = spyOn(component.searchEmitter, 'emit');

    // fake method call
    component.searchTyping('a');
    
    expect(updateTermsSpy).toHaveBeenCalledOnceWith('a');
    expect(component.searchTerms).toEqual('a');
    expect(pageEmitterSpy).toHaveBeenCalledOnceWith('a');

  });
});
