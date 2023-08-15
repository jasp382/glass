import { INITIAL_STATE } from "./reducers";
import {
	selectAlertMessage,
	selectAllContribs,
	selectContribution,
	selectDateRange,
	selectEvent,
	selectHasAlert,
	selectLanguage,
	selectRealEvent,
	selectUser,
	selectUserContribs
} from "./selectors";

describe('TS62 Redux selectors', () => {
	it('T62.1 should have alert message selector', () => {
		let state: any = INITIAL_STATE;
		let selector = jasmine.createSpy('selector', selectAlertMessage).and.callThrough();
		// call
		let result = selectAlertMessage(state);
		// expectation
		expect(typeof selector).toBe('function');
		expect(result).toEqual({ type: '', message: '' });
	});

	it('T62.2 should have has alert selector', () => {
		let state: any = INITIAL_STATE;
		let selector = jasmine.createSpy('selector', selectHasAlert).and.callThrough();
		// call
		let result = selectHasAlert(state);
		// expectation
		expect(typeof selector).toBe('function');
		expect(result).toEqual(false);
	});

	it('T62.3 should have contribution selector', () => {
		let state: any = INITIAL_STATE;
		let selector = jasmine.createSpy('selector', selectContribution).and.callThrough();
		// call
		let result = selectContribution(state);
		// expectation
		expect(typeof selector).toBe('function');
		expect(result).toEqual({ allContributions: [], userContributions: [], });
	});

	it('T62.4 should have all contributions selector', () => {
		let state: any = INITIAL_STATE;
		let selector = jasmine.createSpy('selector', selectAllContribs).and.callThrough();
		// call
		let result = selectAllContribs(state);
		// expectation
		expect(typeof selector).toBe('function');
		expect(result).toEqual([]);
	});

	it('T62.5 should have user contributions selector', () => {
		let state: any = INITIAL_STATE;
		let selector = jasmine.createSpy('selector', selectUserContribs).and.callThrough();
		// call
		let result = selectUserContribs(state);
		// expectation
		expect(typeof selector).toBe('function');
		expect(result).toEqual([]);
	});

	it('T62.6 should have event selector', () => {
		let state: any = INITIAL_STATE;
		let selector = jasmine.createSpy('selector', selectEvent).and.callThrough();
		// call
		let result = selectEvent(state);
		// expectation
		expect(typeof selector).toBe('function');
		expect(result).toEqual({ serviceLayers: [], events: [] });
	});

	it('T62.7 should have real event selector', () => {
		let state: any = INITIAL_STATE;
		let selector = jasmine.createSpy('selector', selectEvent).and.callThrough();
		// call
		let result = selectRealEvent(state);
		// expectation
		expect(typeof selector).toBe('function');
		expect(result).toEqual({ events: [] });
	});

	it('T62.8 should have user selector', () => {
		let state: any = INITIAL_STATE;
		let selector = jasmine.createSpy('selector', selectUser).and.callThrough();
		// call
		let result = selectUser(state);
		// expectation
		expect(typeof selector).toBe('function');
		expect(result).toEqual({});
	});

	it('T62.9 should have date range selector', () => {
		let state: any = INITIAL_STATE;
		let selector = jasmine.createSpy('selector', selectDateRange);
		// call
		selectDateRange(state);
		// expectation
		expect(typeof selector).toBe('function');
	});

	it('T62.10 should have language selector', () => {
		let state: any = INITIAL_STATE;
		let selector = jasmine.createSpy('selector', selectLanguage).and.callThrough();
		// call
		let result = selectLanguage(state);
		// expectation
		expect(typeof selector).toBe('function');
		expect(result).toEqual('pt');
	});
});