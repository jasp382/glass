import { NgRedux } from "@angular-redux/store";
import { MockNgRedux } from "@angular-redux/store/testing";
import { AlertActions } from "./alertActions";

describe('TS45 Redux AlertActions', () => {
    let mockNgRedux: NgRedux<any>;
    let alertActions: AlertActions;

    beforeEach(() => {
        MockNgRedux.reset();
        mockNgRedux = MockNgRedux.getInstance();
        alertActions = new AlertActions(mockNgRedux);
    });

    it('T45.1 should dispatch add alert action', () => {
        // expected action and spy
        const expectedAction = {
            type: AlertActions.ADD_ALERT,
            payload: {
                type: 'success',
                message: 'Email enviado! <strong>Verifique o seu email</strong> para recuperar a sua conta.'
            }
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        alertActions.addAlert('success', 'Email enviado! <strong>Verifique o seu email</strong> para recuperar a sua conta.');

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T45.2 should dispatch reset alert', () => {
        // expected action and spy
        const expectedAction = { type: AlertActions.RESET_ALERT };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        alertActions.resetAlert();

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });
});