import { tassign } from "tassign";
import { ContributionActions } from "../actions/contributionActions";
import { ContributionDateGroup } from "src/app/interfaces/contribs";

/**
 * Interface used for Contribution state in Redux. 
 */
interface ContributionState {
    /**
     * list of all contributions stored
     */
    allContributions: ContributionDateGroup[],
    /**
     * list of user contributions stored
     */
    userContributions: ContributionDateGroup[],
}

/**
 * Initial Contribution state in Redux.
 * Initializes state with empty lists.
 */
const INITIAL_STATE_CONTRIB: ContributionState = { allContributions: [], userContributions: [] };

/**
 * Redux contribution reducer.
 * Checks dispatched action and updates the contribution state with provided payload.
 * 
 * See {@link ContributionActions} for possible actions.
 * @param state Redux Contribution State. If none provided, initial state is used.
 * @param action dispatched action from redux
 * @returns new contribution state
 */
function contributionReducer(state: ContributionState = INITIAL_STATE_CONTRIB, action: any) {
    switch (action.type) {
        // save contributions in redux
        case ContributionActions.SAVE_ALL_CONTRIBS: return tassign(state, { allContributions: action.payload.contribs });
        case ContributionActions.SAVE_USER_CONTRIBS: return tassign(state, { userContributions: action.payload.contribs });
        // remove contributions from redux
        case ContributionActions.REMOVE_ALL_CONTRIBS: return tassign(state, { allContributions: <ContributionDateGroup[]>[] });
        case ContributionActions.REMOVE_USER_CONTRIBS: return tassign(state, { userContributions: <ContributionDateGroup[]>[] });
        default: return state;
    }
}

export { ContributionState, contributionReducer, INITIAL_STATE_CONTRIB };