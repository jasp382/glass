import { ComponentFixture, TestBed } from '@angular/core/testing';

// Components
import { PaginationComponent } from './pagination.component';

// Angular Bootstrap
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
  
describe('TS23 PaginationComponent', () => {
  let component: PaginationComponent;
  let fixture: ComponentFixture<PaginationComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PaginationComponent],
      imports: [
        NgbModule
      ]
    }).compileComponents();

    // component for testing
    fixture = TestBed.createComponent(PaginationComponent);
    component = fixture.componentInstance;

    // default dummy data for input
    component.rowCount = 10;

    // trigger initial data binding
    fixture.detectChanges();
  });

  it('T23.1 should create', () => {
    expect(component).toBeTruthy();
  });

  // testing inputs
  it('T23.2 should have correct initial values', () => {
    expect(component.page).toBe(1);
    expect(component.rowCount).toBe(10);
  });

  it('T23.3 should have correct row count input', () => {
    component.rowCount = 100;
    fixture.detectChanges();
    expect(component.rowCount).toBe(100);

    component.rowCount = 20;
    fixture.detectChanges();
    expect(component.rowCount).toBe(20);
  });

  // testing update page
  it('T23.4 should emit value', () => {
    // setup spies
    const updatePageSpy = spyOn(component, 'updatePage').and.callThrough();
    const pageEmitterSpy = spyOn(component.pageEmitter, 'emit');

    // fake method call
    component.updatePage();

    expect(updatePageSpy).toHaveBeenCalled();
    expect(pageEmitterSpy).toHaveBeenCalledWith(1);
  });

});
