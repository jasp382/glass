import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListUsersAdminComponent } from './list-users-admin.component';

describe('ListUsersAdminComponent', () => {
  let component: ListUsersAdminComponent;
  let fixture: ComponentFixture<ListUsersAdminComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ListUsersAdminComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListUsersAdminComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
