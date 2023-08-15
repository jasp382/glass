import { Component, OnInit } from '@angular/core';

import { Store } from '@ngrx/store';
import { Observable } from 'rxjs';
import { UserModel } from '../models/UsersModel';

import { AppState } from '../stores/app-state';
import * as fromUsersAction from '../stores/users/user.actions';
import * as fromUsersSelector from '../stores/users/user.reducer';

@Component({
  selector: 'app-list-users-admin',
  templateUrl: './list-users-admin.component.html',
  styleUrls: ['./list-users-admin.component.scss']
})
export class ListUsersAdminComponent {

  // Option 1
  listUsers$ : Observable<UserModel[]> = this.store.select(fromUsersSelector.getUsersAdmin);
  // Option 2
  listUsers: UserModel[] = [];

  // Option 3
  listUsers3: UserModel[] = [];

  // Option 4
  listUsers4: UserModel[] = [];

  // Option 5
  listUsers5$ : Observable<UserModel[]> = this.store.select(
    fromUsersSelector.getUsersAdmin, {profile: 'admin'});

  constructor(
    //private userService: UserService
    private store: Store<AppState>
  ) {  }

  ngOnInit(): void {
    // Option 2
    this.store
      .select(fromUsersSelector.getUsersAdmin)
      .subscribe((users: UserModel[])=>{
        this.listUsers = users;
    });

    // Option 3
    this.store
      .select(fromUsersSelector.getUsers)
      .subscribe((users: UserModel[])=>{
        this.listUsers3 = users.filter((filter)=>filter.profile == 'admin');
    });

    // Option 4
    this.store
      .select(fromUsersSelector.getUsersParam, {profile: 'admin'})
      .subscribe((users: UserModel[])=>{
        this.listUsers4 = users;
    });
    
  }

}
