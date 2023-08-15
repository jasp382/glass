import { Component } from '@angular/core';
import { UserModel } from '../models/UsersModel';
import { UserService } from '../repository/UserService';
import { Store } from '@ngrx/store';
import { AppState } from '../stores/app-state';
import * as fromUserAction from '../stores/users/user.actions';

@Component({
  selector: 'app-add-users',
  templateUrl: './add-users.component.html',
  styleUrls: ['./add-users.component.scss']
})
export class AddUsersComponent {
  model: UserModel = {id: 0, name: '', age : 0, profile: ''};

  constructor(private store: Store<AppState>) { }

  addUser() {
    //console.log(this.model);
    if (this.model.id == 0) {
      // Add new user
      //this.userService.addUser(this.model).subscribe();
      this.store.dispatch(fromUserAction.AddUser({payload:this.model}));
    } else {
      // update user
      this.store.dispatch(fromUserAction.UpdateUser({payload: this.model}));
    }
  }

}
