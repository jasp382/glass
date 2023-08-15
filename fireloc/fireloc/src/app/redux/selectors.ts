import { AppState } from "./reducers";

// --------- alert selectors
/**
 * Redux selector for alert message. Used for user feedback.
 * @param state Redux App State
 * @returns alert message state
 */
export const selectAlertMessage = (state: AppState) => state.alert.alertMessage;
/**
 * Redux selector for has alert value. Used for user feedback.
 * @param state Redux App State
 * @returns has alert state
 */
export const selectHasAlert = (state: AppState) => state.alert.hasAlert;

// --------- contribution selectors
/**
 * Redux selector for contributions state. Used for date range.
 * @param state Redux App State
 * @returns contribution state
 */
export const selectContribution = (state: AppState) => state.contribution;
/**
 * Redux selector for all contributions state. Used for contributions.
 * @param state Redux App State
 * @returns all contributions state
 */
export const selectAllContribs = (state: AppState) => state.contribution.allContributions;
/**
 * Redux selector for user contributions state. Used for contributions.
 * @param state Redux App State
 * @returns user contributions state
 */
export const selectUserContribs = (state: AppState) => state.contribution.userContributions;

// --------- event selectors
/**
 * Redux selector for event state. Used for events and date range.
 * @param state Redux App State
 * @returns event state
 */
export const selectEvent = (state: AppState) => state.event;
/**
 * Redux selector for real event state. Used for real events.
 * @param state Redux App State
 * @returns real event state
 */
export const selectRealEvent = (state: AppState) => state.realEvent;

// --------- user selectors
/**
 * Redux selector for user state. Used to update user information without page reload.
 * @param state Redux App State
 * @returns user state
 */
export const selectUser = (state: AppState) => state.user;

// --------- date range selector
/**
 * Redux selector for date range state. Used to get updates on date range for events and contributions.
 * @param state Redux App State
 * @returns date range state
 */
export const selectDateRange = (state: AppState) => state.dateRange;

// --------- language selector
/**
 * Redux selector for language state. Used to get updates on language used in the app.
 * @param state Redux App State
 * @returns language state
 */
export const selectLanguage = (state: AppState) => state.language.language;