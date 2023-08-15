import { Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs';
import { UserModel } from '../models/UsersModel';
//import { UserService } from '../repository/UserService';
import { AppState } from '../stores/app-state';
import * as fromUsersAction from '../stores/users/user.actions';
import * as fromUsersSelector from '../stores/users/user.reducer';

@Component({
  selector: 'app-list-users',
  templateUrl: './list-users.component.html',
  styleUrls: ['./list-users.component.scss']
})
export class ListUsersComponent implements OnInit {
  //listUsers: UserModel[] = [];
  listUsers$ : Observable<UserModel[]> = this.store.select(fromUsersSelector.getUsers);

  user$ : Observable<UserModel | null> = this.store.select(fromUsersSelector.getUser);
  
  constructor(
    //private userService: UserService
    private store: Store<AppState>
  ) {  }

  ngOnInit(): void {
    this.store.dispatch(fromUsersAction.LoadUsers());
    //this.userService.getUsers().subscribe((users: UserModel[]) => {
      //this.listUsers = users;
    //});
  }

  editUser(id: number) {
    this.store.dispatch(fromUsersAction.LoadUser({payload:id}));
  }

  delUser(id: number) {
    this.store.dispatch(fromUsersAction.DeleteUser({payload:id}));
  }

}
