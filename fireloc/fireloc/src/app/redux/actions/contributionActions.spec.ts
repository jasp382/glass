import { NgRedux } from "@angular-redux/store";
import { MockNgRedux } from "@angular-redux/store/testing";
import { ContributionDateGroup } from "src/app/interfaces/contribs";
import { ContributionActions } from "./contributionActions";

describe('TS46 Redux ContributionActions', () => {
    let mockNgRedux: NgRedux<any>;
    let contribActions: ContributionActions;

    beforeEach(() => {
        MockNgRedux.reset();
        mockNgRedux = MockNgRedux.getInstance();
        contribActions = new ContributionActions(mockNgRedux);
    });

    it('T46.1 should dispatch save all contributions', () => {
        // expected action and spy
        const expectedAction = {
            type: ContributionActions.SAVE_ALL_CONTRIBS,
            payload: {
                contribs: [] as ContributionDateGroup[]
            }
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        contribActions.saveAllContributions([] as ContributionDateGroup[]);

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T46.2 should dispatch save user contributions', () => {
        // expected action and spy
        const expectedAction = {
            type: ContributionActions.SAVE_USER_CONTRIBS,
            payload: {
                contribs: [] as ContributionDateGroup[]
            }
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        contribActions.saveUserContributions([] as ContributionDateGroup[]);

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T46.3 should dispatch remove all contributions', () => {
        // expected action and spy
        const expectedAction = { type: ContributionActions.REMOVE_ALL_CONTRIBS };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        contribActions.removeAllContributions();

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T46.4 should dispatch remove user contributions', () => {
        // expected action and spy
        const expectedAction = { type: ContributionActions.REMOVE_USER_CONTRIBS };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        contribActions.removeUserContributions();

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

});