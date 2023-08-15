import { Injectable } from '@angular/core';
import { NgRedux } from '@angular-redux/store';
import { AppState } from '../reducers';

/**
 * Redux user actions. 
 * These actions are meant to be dispatched and caught by {@link userReducer}.
 */
@Injectable()
export class UserActions {
	/**
	 * Action to update logged user information in the UI
	 */
	static GET_USER_INFO = 'GET_USER_INFO';

	/**
	 * Empty constructor
	 * @param ngRedux Redux to dispatch actions
	 */
	constructor(private ngRedux: NgRedux<AppState>) { }

	/**
	 * Dispatch the action to get user information
	 */
	getUserInfo() {
		this.ngRedux.dispatch({ type: UserActions.GET_USER_INFO });
	}

}