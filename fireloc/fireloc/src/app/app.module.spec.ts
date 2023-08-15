import { NgRedux, DevToolsExtension } from '@angular-redux/store';
import { NgReduxTestingModule, MockNgRedux, MockDevToolsExtension } from '@angular-redux/store/testing';
import { TestBed, getTestBed } from '@angular/core/testing';
import { AppModule } from './app.module';


describe('TS2 App Module', () => {
	let mockNgRedux: NgRedux<any>;
	let devTools: DevToolsExtension;

	beforeEach(() => {
		TestBed.configureTestingModule({
			imports: [NgReduxTestingModule],
			providers: [MockDevToolsExtension]
		}).compileComponents();

		const testbed = getTestBed();
		devTools = testbed.inject(MockDevToolsExtension);
		mockNgRedux = MockNgRedux.getInstance();
	});

	it('T2.1 should configure the store when the module is loaded', () => {
		const configureSpy = spyOn(MockNgRedux.getInstance(), 'configureStore');
		const instance = new AppModule(mockNgRedux, devTools);
	
		expect(configureSpy).toHaveBeenCalled();
	});

	it('T2.2 should configure the store when the module is loaded (enabled dev tools)', () => {
		let enabledSpy = spyOn(devTools, 'isEnabled').and.returnValue(true);
		let enhancerSpy = spyOn(devTools, 'enhancer');

		const configureSpy = spyOn(MockNgRedux.getInstance(), 'configureStore');
		const instance = new AppModule(mockNgRedux, devTools);
	
		expect(configureSpy).toHaveBeenCalled();
		expect(enabledSpy).toHaveBeenCalled();
		expect(enhancerSpy).toHaveBeenCalled();
	});
});