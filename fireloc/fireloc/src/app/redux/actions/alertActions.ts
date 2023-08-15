import { Injectable } from '@angular/core';
import { NgRedux } from '@angular-redux/store';
import { AppState } from '../reducers';

/**
 * Redux alert actions. 
 * These actions are meant to be dispatched and caught by {@link alertReducer}.
 */
@Injectable()
export class AlertActions {
	/**
	 * Action to add a new alert to the UI.
	 */
	static ADD_ALERT = 'ADD_ALERT';
	/**
	 * Action to remove an alert from the UI.
	 */
	static RESET_ALERT = 'RESET_ALERT';

	/**
	 * Empty constructor
	 * @param ngRedux Redux to dispatch actions
	 */
	constructor(private ngRedux: NgRedux<AppState>) { }

	/**
	 * Dispatch action to display an alert of a desired type with a desired message.
	 * @param type alert type
	 * @param message alert message
	 */
	addAlert(type: string, message: string) {
		this.ngRedux.dispatch({ type: AlertActions.ADD_ALERT, payload: { type: type, message: message } });
	}

	/**
	 * Dispatch action to remove an alert from the UI and reset the state
	 */
	resetAlert() {
		this.ngRedux.dispatch({ type: AlertActions.RESET_ALERT });
	}
}