// Testing
import { MockNgRedux, NgReduxTestingModule } from '@angular-redux/store/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';

// Redux
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';
import { LayerActions } from 'src/app/redux/actions/layerActions';

// Constants
import { routes } from 'src/app/app-routing.module';

// Component
import { LayersbarComponent } from './layersbar.component';
import { Layer } from 'src/app/interfaces/layers';
import { of, throwError } from 'rxjs';

describe('TS37 LayersbarComponent', () => {
  let component: LayersbarComponent;
  let fixture: ComponentFixture<LayersbarComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        LayersbarComponent,
      ],
      imports: [
        RouterTestingModule.withRoutes(routes),
        HttpClientTestingModule,
        NgReduxTestingModule,
      ],
      providers: [
        ContributionActions,
        LayerActions,
        EventActions,
      ],
    }).compileComponents();

    // reset redux
    MockNgRedux.reset();

    fixture = TestBed.createComponent(LayersbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T37.1 should create', () => {
    expect(component).toBeTruthy();
  });

  it('T37.2 should get layers with token if user is logged in', () => {
    // spy and setup
    let layersTokenSpy = spyOn(component, 'getLayersToken');
    component.isLoggedIn = true;
    component.ngOnInit();

    expect(layersTokenSpy).toHaveBeenCalled();
  });

  it('T37.3 should get layers without token if user is not logged in', () => {
    // spy and setup
    let layersNoTokenSpy = spyOn(component, 'getLayersNoToken');
    component.isLoggedIn = false;
    component.ngOnInit();

    expect(layersNoTokenSpy).toHaveBeenCalled();
  });

  it('T37.4 should get layers without token', () => {
    // spies
    let layersNoTokenSpy = spyOn(component, 'getLayersNoToken').and.callThrough();
    let layerServSpy = spyOn(component['layerServ'], 'getLayersNoToken')
      .and.returnValue(of({ data: [] }));
    let layersInfoSpy = spyOn(component, 'getLayersInformation');

    // call method
    component.getLayersNoToken();

    // expectations
    expect(layersNoTokenSpy).toHaveBeenCalledOnceWith();
    expect(layerServSpy).toHaveBeenCalledOnceWith();
    expect(layersInfoSpy).toHaveBeenCalledOnceWith([]);
  });

  it('T37.5 should handle error getting layers without token', () => {
    // spies
    let layersNoTokenSpy = spyOn(component, 'getLayersNoToken').and.callThrough();
    let layerServSpy = spyOn(component['layerServ'], 'getLayersNoToken')
      .and.returnValue(throwError(() => new Error('oops')));
    let layersInfoSpy = spyOn(component, 'getLayersInformation');

    // call method
    component.getLayersNoToken();

    // expectations
    expect(layersNoTokenSpy).toHaveBeenCalledOnceWith();
    expect(layerServSpy).toHaveBeenCalledOnceWith();
    expect(layersInfoSpy).not.toHaveBeenCalled();
  });

  it('T37.6 should get layers with token', () => {
    // spies
    let layersTokenSpy = spyOn(component, 'getLayersToken').and.callThrough();
    let layerServSpy = spyOn(component['layerServ'], 'getLayersToken')
      .and.returnValue(of({ data: [] }));
    let layersInfoSpy = spyOn(component, 'getLayersInformation');

    // call method
    component.getLayersToken();

    // expectations
    expect(layersTokenSpy).toHaveBeenCalledOnceWith();
    expect(layerServSpy).toHaveBeenCalledOnceWith();
    expect(layersInfoSpy).toHaveBeenCalledOnceWith([]);
  });

  it('T37.7 should handle error getting layers with token', () => {
    // spies
    let layersTokenSpy = spyOn(component, 'getLayersToken').and.callThrough();
    let layerServSpy = spyOn(component['layerServ'], 'getLayersToken')
      .and.returnValue(throwError(() => new Error('oops')));
    let layersInfoSpy = spyOn(component, 'getLayersInformation');

    // call method
    component.getLayersToken();

    // expectations
    expect(layersTokenSpy).toHaveBeenCalledOnceWith();
    expect(layerServSpy).toHaveBeenCalledOnceWith();
    expect(layersInfoSpy).not.toHaveBeenCalled();
  });

  it('T37.8 should get layer information from API result', () => {
    // spy and fake data
    let getInfoSpy = spyOn(component, 'getLayersInformation').and.callThrough();
    let fakeLayersResult = [{
      id: 1,
      level: 1,
      designation: 'design',
      gsrvlyr: 'serverLayer',
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace',
      child: null
    }];

    // call method
    component.getLayersInformation(fakeLayersResult);

    // expectations
    expect(getInfoSpy).toHaveBeenCalledOnceWith(fakeLayersResult);
    expect(component.categories).toEqual([{
      id: 1,
      level: 1,
      title: 'design',
      serverLayer: 'serverLayer',
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace',
      isOpen: false,
      child: null
    }]);
  });

  it('T37.9 should get layer children from layer', () => {
    // spy and fake data
    let layerChildrenSpy = spyOn(component, 'getLayerChildren').and.callThrough();
    let fakeChildLayer: any[] = [{
      id: 1,
      level: 1,
      title: 'design',
      serverLayer: 'serverLayer',
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace',
      child: [{
        id: 1,
        level: 1,
        title: 'design',
        serverLayer: 'serverLayer',
        slug: 'slug',
        store: 'store',
        style: 'style',
        workspace: 'workspace',
        child: null,
      }]
    }];

    // call method
    component.getLayerChildren(fakeChildLayer);

    // expectations
    expect(layerChildrenSpy).toHaveBeenCalledTimes(3);
    expect(layerChildrenSpy.calls.all()[0].args[0]).toEqual(fakeChildLayer);
    expect(layerChildrenSpy.calls.all()[1].args[0]).toEqual(fakeChildLayer[0].child);
    expect(layerChildrenSpy.calls.all()[2].args[0]).toEqual(null);
  });

  it('T37.10 should open layer category if it is closed', () => {
    // spies and fake data
    let toggleSpy = spyOn(component, 'toggleCategory').and.callThrough();
    let removeReduxSpy = spyOn(component, 'removeChildLayersFromRedux');
    let fakeLayer: Layer = {
      id: 1,
      level: 1,
      title: 'design',
      serverLayer: 'serverLayer',
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace',
      child: null,
      isOpen: false
    };

    // call method
    component.toggleCategory(fakeLayer);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(fakeLayer);
    expect(fakeLayer.isOpen).toBeTrue();
    expect(removeReduxSpy).not.toHaveBeenCalled();
  });

  it('T37.11 should close layer category if it is open', () => {
    // spies and fake data
    let toggleSpy = spyOn(component, 'toggleCategory').and.callThrough();
    let removeReduxSpy = spyOn(component, 'removeChildLayersFromRedux');
    let fakeLayer: Layer = {
      id: 1,
      level: 1,
      title: 'design',
      serverLayer: 'serverLayer',
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace',
      child: null,
      isOpen: true
    };

    // call method
    component.toggleCategory(fakeLayer);

    // expectations
    expect(toggleSpy).toHaveBeenCalledOnceWith(fakeLayer);
    expect(fakeLayer.isOpen).toBeFalse();
    expect(removeReduxSpy).toHaveBeenCalled();
  });

  it('T37.12 should not remove child layers from redux if there is no child', () => {
    // spies and fake data
    let removeReduxSpy = spyOn(component, 'removeChildLayersFromRedux').and.callThrough();
    let noChild = null;

    // call method
    component.removeChildLayersFromRedux(noChild);

    // expectations
    expect(removeReduxSpy).toHaveBeenCalledOnceWith(null);
  });

  it('T37.13 should remove child layers from redux if there are children', () => {
    // spies and fake data
    let removeReduxSpy = spyOn(component, 'removeChildLayersFromRedux').and.callThrough();
    let layerActionsSpy = spyOn(component['layerActions'], 'removeLayer');
    let fakeChildLayer: any[] = [{
      id: 1,
      level: 1,
      title: 'design',
      serverLayer: 'serverLayer',
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace',
      child: [{
        id: 1,
        level: 1,
        title: 'design',
        serverLayer: 'serverLayer',
        slug: 'slug',
        store: 'store',
        style: 'style',
        workspace: 'workspace',
        child: null,
      }]
    }];

    // call method
    component.removeChildLayersFromRedux(fakeChildLayer);

    // expectations
    expect(removeReduxSpy).toHaveBeenCalledTimes(3);
    expect(layerActionsSpy).toHaveBeenCalledTimes(2);

    expect(removeReduxSpy.calls.all()[0].args[0]).toEqual(fakeChildLayer);
    expect(removeReduxSpy.calls.all()[1].args[0]).toEqual(fakeChildLayer[0].child);
    expect(removeReduxSpy.calls.all()[2].args[0]).toEqual(null);

    expect(layerActionsSpy.calls.all()[0].args[0]).toEqual(fakeChildLayer[0]);
    expect(layerActionsSpy.calls.all()[1].args[0]).toEqual(fakeChildLayer[0].child[0]);
  });

  it('T37.14 should add layer to redux if it is checked', () => {
    // spies and fake data
    let onChangeSpy = spyOn(component, 'onChangeLayers').and.callThrough();
    let actionAddSpy = spyOn(component['layerActions'], 'addLayer');
    let actionRemoveSpy = spyOn(component['layerActions'], 'removeLayer');
    let fakeLayer: Layer = {
      id: 1,
      level: 1,
      title: 'design',
      serverLayer: 'serverLayer',
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace',
      child: null,
      isOpen: false
    };
    let fakeEvent = { target: { checked: true } };

    // call method
    component.onChangeLayers(fakeEvent, fakeLayer);

    // expectations
    expect(onChangeSpy).toHaveBeenCalledOnceWith(fakeEvent, fakeLayer);
    expect(actionAddSpy).toHaveBeenCalledOnceWith(fakeLayer);
    expect(actionRemoveSpy).not.toHaveBeenCalled();
  });

  it('T37.15 should remove layer from redux if it is unchecked', () => {
    // spies and fake data
    let onChangeSpy = spyOn(component, 'onChangeLayers').and.callThrough();
    let actionAddSpy = spyOn(component['layerActions'], 'addLayer');
    let actionRemoveSpy = spyOn(component['layerActions'], 'removeLayer');
    let fakeLayer: Layer = {
      id: 1,
      level: 1,
      title: 'design',
      serverLayer: 'serverLayer',
      slug: 'slug',
      store: 'store',
      style: 'style',
      workspace: 'workspace',
      child: null,
      isOpen: false
    };
    let fakeEvent = { target: { checked: false } };

    // call method
    component.onChangeLayers(fakeEvent, fakeLayer);

    // expectations
    expect(onChangeSpy).toHaveBeenCalledOnceWith(fakeEvent, fakeLayer);
    expect(actionAddSpy).not.toHaveBeenCalled();
    expect(actionRemoveSpy).toHaveBeenCalledOnceWith(fakeLayer);
  });

});
