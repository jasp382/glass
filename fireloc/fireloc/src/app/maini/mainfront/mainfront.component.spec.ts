// Testing
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';

// Modules
import { FeatModule } from 'src/app/feat/feat.module';
import { MainiModule } from '../maini.module';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

// Redux
import { NgReduxTestingModule } from '@angular-redux/store/testing';
import { ContributionActions } from 'src/app/redux/actions/contributionActions';
import { EventActions } from 'src/app/redux/actions/eventActions';
import { UserActions } from 'src/app/redux/actions/userActions';
import { DateRangeActions } from 'src/app/redux/actions/dateRangeActions';
import { LayerActions } from 'src/app/redux/actions/layerActions';
import { LangActions } from 'src/app/redux/actions/langActions';

// Services
import { LyrsService } from 'src/app/serv/leafmap/lyrs.service';
import { MarkerService } from 'src/app/serv/leafmap/marker.service';
import { ContributionLayersService } from 'src/app/serv/rest/geo/contribution-layers.service';
import { AuthService } from 'src/app/serv/rest/users/auth.service';

import { MainfrontComponent } from './mainfront.component';
import { routes } from 'src/app/app-routing.module';
import { of, throwError } from 'rxjs';

// Translate
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { httpTranslateLoader } from 'src/app/app.module';
import { HttpClient } from '@angular/common/http';

describe('TS40 MainfrontComponent', () => {
  let component: MainfrontComponent;
  let fixture: ComponentFixture<MainfrontComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MainfrontComponent],
      imports: [
        HttpClientTestingModule,
        RouterTestingModule.withRoutes(routes),
        NgReduxTestingModule,
        FeatModule,
        MainiModule,
        FontAwesomeModule,
        TranslateModule.forRoot({
          loader: {
            provide: TranslateLoader,
            useFactory: httpTranslateLoader,
            deps: [HttpClient]
          }
        }),
      ],
      providers: [
        AuthService,
        ContributionLayersService,
        MarkerService,
        LyrsService,
        ContributionActions,
        EventActions,
        UserActions,
        DateRangeActions,
        LayerActions,
        LangActions
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(MainfrontComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T40.1 should create', () => { expect(component).toBeTruthy(); });

  it('T40.2 should request contribution layers if user is logged in', () => {
    let requestSpy = spyOn(component, 'requestContribLayers');

    component.isLoggedIn = true;
    fixture.detectChanges();

    component.ngOnInit();
    expect(requestSpy).toHaveBeenCalled();
    expect(component.isLoggedIn).toBeTrue();
    expect(component.hasPermission).toBeTrue();
  });

  it('T40.3 should not request contribution layers if user is not logged in', () => {
    let requestSpy = spyOn(component, 'requestContribLayers');

    component.isLoggedIn = false;
    fixture.detectChanges();

    component.ngOnInit();
    expect(requestSpy).not.toHaveBeenCalled();
    expect(component.isLoggedIn).toBeFalse();
    expect(component.hasPermission).toBeFalse();
  });

  it('T40.4 should open left panel menu', () => {
    let toggleSpy = spyOn(component, 'toggleLeftPanel').and.callThrough();
    component.isLeftOpen = false;
    fixture.detectChanges();

    component.toggleLeftPanel();
    expect(toggleSpy).toHaveBeenCalled();
    expect(component.isLeftOpen).toBeTrue();
  });

  it('T40.5 should close left panel menu', () => {
    let toggleSpy = spyOn(component, 'toggleLeftPanel').and.callThrough();

    component.toggleLeftPanel();
    expect(toggleSpy).toHaveBeenCalled();
    expect(component.isLeftOpen).toBeFalse();
  });

  it('T40.6 should get contribution layers from API', () => {
    let requestSpy = spyOn(component, 'requestContribLayers').and.callThrough();
    let APISpy = spyOn(component['contribLayersServ'], 'getContribLayers').and.returnValue(of({
      data: [{
        id: 1,
        slug: 'slug',
        designation: 'design',
        workspace: 'work',
        store: 'store',
        level: 1,
        gsrvlyr: 'layer',
        minzoom: 1,
        maxzoom: 2,
      }]
    }));
    let getDataSpy = spyOn(component, 'getMapContribLayersData').and.callThrough();

    component.requestContribLayers();
    expect(requestSpy).toHaveBeenCalled();
    expect(APISpy).toHaveBeenCalled();
    expect(getDataSpy).toHaveBeenCalled();
  });

  it('T40.7 should handle error from getting contribution layers from API', () => {
    let requestSpy = spyOn(component, 'requestContribLayers').and.callThrough();
    let APISpy = spyOn(component['contribLayersServ'], 'getContribLayers').and.returnValue(throwError(() => new Error()));
    let getDataSpy = spyOn(component, 'getMapContribLayersData').and.callThrough();

    component.requestContribLayers();
    expect(requestSpy).toHaveBeenCalled();
    expect(APISpy).toHaveBeenCalled();
    expect(getDataSpy).not.toHaveBeenCalled();
  });

  it('T40.8 should not set geoportal map listeners if map is null', () => {
    let receiveSpy = spyOn(component, 'receiveMap').and.callThrough();
    component.receiveMap(null);
    expect(receiveSpy).toHaveBeenCalled();
    expect(component.map).toBeNull();
  });

  it('T40.9 should detect zoom changes on geoportal map', () => {
    let zoomSpy = spyOn(component, 'getMapZoom');

    component.map?.fireEvent('zoomend');

    // expectations
    expect(component.map).not.toBeNull();
    expect(zoomSpy).toHaveBeenCalled();
  });

  it('T40.10 should detect move changes on geoportal map', () => {
    let moveSpy = spyOn(component, 'getMapBounds');

    component.map?.fireEvent('moveend');

    // expectations
    expect(component.map).not.toBeNull();
    expect(moveSpy).toHaveBeenCalled();
  });

  it('T40.11 should get map bounds', () => {
    let boundSpy = spyOn(component, 'getMapBounds').and.callThrough();
    let contribSpy = spyOn(component, 'getContribLayerZoom');

    component.getMapBounds();

    // expectations
    expect(component.map).not.toBeNull();
    expect(boundSpy).toHaveBeenCalled();
    expect(contribSpy).toHaveBeenCalled();
  });

  it('T40.12 should check if map is not null before getting bounding box', () => {
    // just for coverage purposes
    component.map = null;
    fixture.detectChanges();

    let boundSpy = spyOn(component, 'getMapBounds').and.callThrough();
    let contribSpy = spyOn(component, 'getContribLayerZoom');

    component.getMapBounds();

    // expectations
    expect(component.map).toBeNull();
    expect(boundSpy).toHaveBeenCalled();
    expect(contribSpy).toHaveBeenCalled();
  });

  it('T40.13 should get map zoom', () => {
    let zoomSpy = spyOn(component, 'getMapZoom').and.callThrough();
    let contribSpy = spyOn(component, 'getContribLayerZoom');

    component.getMapZoom();

    // expectations
    expect(component.map).not.toBeNull();
    expect(zoomSpy).toHaveBeenCalled();
    expect(contribSpy).toHaveBeenCalled();
  });

  it('T40.14 should check if map is not null before getting map zoom', () => {
    // just for coverage purposes
    component.map = null;
    fixture.detectChanges();

    let zoomSpy = spyOn(component, 'getMapZoom').and.callThrough();
    let contribSpy = spyOn(component, 'getContribLayerZoom');

    component.getMapZoom();

    // expectations
    expect(component.map).toBeNull();
    expect(zoomSpy).toHaveBeenCalled();
    expect(contribSpy).toHaveBeenCalled();
  });

  it('T40.15 should get active tab for right menu', () => {
    let receiveSpy = spyOn(component, 'receiveActiveRightTab').and.callThrough();
    let removeSpy = spyOn(component['mapLayerServ'], 'removeLayer');

    component.receiveActiveRightTab(2);
    component.receiveActiveRightTab(0);

    expect(receiveSpy).toHaveBeenCalled();
    expect(component.activeRightTab).toBe(0);
    expect(component.map).not.toBeNull();
    expect(removeSpy).not.toHaveBeenCalled();
  });

  it('T40.16 should remove contribution clusters from map if another right tab is active', () => {
    let receiveSpy = spyOn(component, 'receiveActiveRightTab').and.callThrough();
    let removeSpy = spyOn(component['mapLayerServ'], 'removeLayer');

    component.receiveActiveRightTab(1);

    expect(receiveSpy).toHaveBeenCalled();
    expect(component.activeRightTab).toBe(1);
    expect(component.map).not.toBeNull();
    expect(removeSpy).toHaveBeenCalled();
  });

  it('T40.17 should get contributions option from contribution component (all or user)', () => {
    let receiveSpy = spyOn(component, 'receiveContribOption').and.callThrough();
    let zoomSpy = spyOn(component, 'getMapZoom');

    component.mapCurrentZoom = 3;
    fixture.detectChanges();

    component.receiveContribOption(true);

    expect(receiveSpy).toHaveBeenCalled();
    expect(component.showingAllContribs).toBeTrue();
    expect(zoomSpy).not.toHaveBeenCalled();
  });

  it('T40.18 should get zoom after contributions option if zoom is unchanged', () => {
    let receiveSpy = spyOn(component, 'receiveContribOption').and.callThrough();
    let zoomSpy = spyOn(component, 'getMapZoom');

    component.receiveContribOption(true);

    expect(receiveSpy).toHaveBeenCalled();
    expect(component.showingAllContribs).toBeTrue();
    expect(zoomSpy).toHaveBeenCalled();
  });

  it('T40.19 should get contribution layer according to map zoom (first level - no bounds)', () => {
    component.mapCurrentZoom = 2;
    component.mapContribLayers = [{
      id: 1, level: 1, slug: 'slug1', designation: 'design1', workspace: 'work1',
      store: 'store1', serverLayer: 'server1', minZoom: 1, maxZoom: 2,
    }, {
      id: 2, level: 2, slug: 'slug2', designation: 'design2', workspace: 'work2',
      store: 'store2', serverLayer: 'server2', minZoom: 3, maxZoom: 4,
    },];
    fixture.detectChanges();

    let contribSpy = spyOn(component, 'getContribLayerZoom').and.callThrough();
    let layerSpy = spyOn(component, 'getContribLayer');

    component.getContribLayerZoom();

    expect(contribSpy).toHaveBeenCalledOnceWith();
    expect(layerSpy).toHaveBeenCalledOnceWith('work1', 'server1');
  });

  it('T40.20 should get contribution layer according to map zoom (second level - no bounds)', () => {
    component.mapCurrentZoom = 3;
    component.mapContribLayers = [{
      id: 1, level: 1, slug: 'slug1', designation: 'design1', workspace: 'work1',
      store: 'store1', serverLayer: 'server1', minZoom: 1, maxZoom: 2,
    }, {
      id: 2, level: 2, slug: 'slug2', designation: 'design2', workspace: 'work2',
      store: 'store2', serverLayer: 'server2', minZoom: 3, maxZoom: 4,
    },];
    fixture.detectChanges();

    let contribSpy = spyOn(component, 'getContribLayerZoom').and.callThrough();
    let layerSpy = spyOn(component, 'getContribLayer');
    let boundsSpy = spyOn(component, 'getMapBounds');

    component.getContribLayerZoom();

    expect(contribSpy).toHaveBeenCalledOnceWith();
    expect(layerSpy).toHaveBeenCalledOnceWith('work2', 'server2', undefined);
    expect(boundsSpy).toHaveBeenCalledOnceWith();
  });

  it('T40.21 should get contribution layer according to map zoom (second level - existing bounds)', () => {
    component.mapCurrentZoom = 3;
    component.mapBoundsWKT = '';
    component.mapContribLayers = [{
      id: 1, level: 1, slug: 'slug1', designation: 'design1', workspace: 'work1',
      store: 'store1', serverLayer: 'server1', minZoom: 1, maxZoom: 2,
    }, {
      id: 2, level: 2, slug: 'slug2', designation: 'design2', workspace: 'work2',
      store: 'store2', serverLayer: 'server2', minZoom: 3, maxZoom: 4,
    },];
    fixture.detectChanges();

    let contribSpy = spyOn(component, 'getContribLayerZoom').and.callThrough();
    let layerSpy = spyOn(component, 'getContribLayer');
    let boundsSpy = spyOn(component, 'getMapBounds');

    component.getContribLayerZoom();

    expect(contribSpy).toHaveBeenCalledOnceWith();
    expect(layerSpy).toHaveBeenCalledOnceWith('work2', 'server2', '');
    expect(boundsSpy).not.toHaveBeenCalledOnceWith();
  });

  it('T40.22 should get contribution cluster data (no bounding box)', () => {
    let layerSpy = spyOn(component, 'getContribLayer').and.callThrough();
    let contribAPISpy = spyOn(component['contribLayersServ'], 'getWebFeatureService').and.returnValue(of({ data: {} }));
    let mapLayerRemoveSpy = spyOn(component['mapLayerServ'], 'removeLayer');
    let mapLayerAddSpy = spyOn(component['mapLayerServ'], 'addLayer');
    let markerSpy = spyOn(component['markerServ'], 'addGeoLayerToCluster');

    component.getContribLayer('', '');

    expect(layerSpy).toHaveBeenCalled();
    expect(contribAPISpy).toHaveBeenCalledOnceWith('', '');
    expect(mapLayerRemoveSpy).toHaveBeenCalled();
    expect(markerSpy).toHaveBeenCalled();
    expect(mapLayerAddSpy).toHaveBeenCalled();
  });

  it('T40.23 should get contribution cluster data (no bounding box, no map)', () => {
    component.map = null;
    fixture.detectChanges();

    let layerSpy = spyOn(component, 'getContribLayer').and.callThrough();
    let contribAPISpy = spyOn(component['contribLayersServ'], 'getWebFeatureService').and.returnValue(of({ data: {} }));
    let mapLayerRemoveSpy = spyOn(component['mapLayerServ'], 'removeLayer');
    let mapLayerAddSpy = spyOn(component['mapLayerServ'], 'addLayer');
    let markerSpy = spyOn(component['markerServ'], 'addGeoLayerToCluster');

    component.getContribLayer('', '');

    expect(layerSpy).toHaveBeenCalled();
    expect(contribAPISpy).toHaveBeenCalledOnceWith('', '');
    expect(mapLayerRemoveSpy).not.toHaveBeenCalled();
    expect(markerSpy).toHaveBeenCalled();
    expect(mapLayerAddSpy).not.toHaveBeenCalled();
  });

  it('T40.24 should handle error from getting contribution cluster data (no bounding box)', () => {
    let layerSpy = spyOn(component, 'getContribLayer').and.callThrough();
    let contribAPISpy = spyOn(component['contribLayersServ'], 'getWebFeatureService').and.returnValue(throwError(() => new Error()));
    let mapLayerRemoveSpy = spyOn(component['mapLayerServ'], 'removeLayer');
    let mapLayerAddSpy = spyOn(component['mapLayerServ'], 'addLayer');
    let markerSpy = spyOn(component['markerServ'], 'addGeoLayerToCluster');

    component.getContribLayer('', '');

    expect(layerSpy).toHaveBeenCalled();
    expect(contribAPISpy).toHaveBeenCalledOnceWith('', '');
    expect(mapLayerRemoveSpy).not.toHaveBeenCalled();
    expect(markerSpy).not.toHaveBeenCalled();
    expect(mapLayerAddSpy).not.toHaveBeenCalled();
  });

  it('T40.25 should get contribution cluster data (bounding box)', () => {
    let layerSpy = spyOn(component, 'getContribLayer').and.callThrough();
    let contribAPISpy = spyOn(component['contribLayersServ'], 'getWebFeatureService').and.returnValue(of({ data: {} }));
    let mapLayerRemoveSpy = spyOn(component['mapLayerServ'], 'removeLayer');
    let mapLayerAddSpy = spyOn(component['mapLayerServ'], 'addLayer');
    let markerSpy = spyOn(component['markerServ'], 'addGeoLayerToCluster');

    component.getContribLayer('', '', 'box');

    expect(layerSpy).toHaveBeenCalled();
    expect(contribAPISpy).toHaveBeenCalledOnceWith('', '', 'box');
    expect(mapLayerRemoveSpy).toHaveBeenCalled();
    expect(markerSpy).toHaveBeenCalled();
    expect(mapLayerAddSpy).toHaveBeenCalled();
  });

  it('T40.26 should get contribution cluster data (bounding box, no map)', () => {
    component.map = null;
    fixture.detectChanges();

    let layerSpy = spyOn(component, 'getContribLayer').and.callThrough();
    let contribAPISpy = spyOn(component['contribLayersServ'], 'getWebFeatureService').and.returnValue(of({ data: {} }));
    let mapLayerRemoveSpy = spyOn(component['mapLayerServ'], 'removeLayer');
    let mapLayerAddSpy = spyOn(component['mapLayerServ'], 'addLayer');
    let markerSpy = spyOn(component['markerServ'], 'addGeoLayerToCluster');

    component.getContribLayer('', '', 'box');

    expect(layerSpy).toHaveBeenCalled();
    expect(contribAPISpy).toHaveBeenCalledOnceWith('', '', 'box');
    expect(mapLayerRemoveSpy).not.toHaveBeenCalled();
    expect(markerSpy).toHaveBeenCalled();
    expect(mapLayerAddSpy).not.toHaveBeenCalled();
  });

  it('T40.27 should handle error from getting contribution cluster data (bounding box)', () => {
    let layerSpy = spyOn(component, 'getContribLayer').and.callThrough();
    let contribAPISpy = spyOn(component['contribLayersServ'], 'getWebFeatureService').and.returnValue(throwError(() => new Error()));
    let mapLayerRemoveSpy = spyOn(component['mapLayerServ'], 'removeLayer');
    let mapLayerAddSpy = spyOn(component['mapLayerServ'], 'addLayer');
    let markerSpy = spyOn(component['markerServ'], 'addGeoLayerToCluster');

    component.getContribLayer('', '', 'box');

    expect(layerSpy).toHaveBeenCalled();
    expect(contribAPISpy).toHaveBeenCalledOnceWith('', '', 'box');
    expect(mapLayerRemoveSpy).not.toHaveBeenCalled();
    expect(markerSpy).not.toHaveBeenCalled();
    expect(mapLayerAddSpy).not.toHaveBeenCalled();
  });

  // TODO UPDATE TESTS WHEN MAP STYLE IMPLEMENTED
  it('T40.28 should change map to style 1', () => {
    let styleSpy = spyOn(component, 'mapStyle1').and.callThrough();
    component.mapStyle1();
    expect(styleSpy).toHaveBeenCalled();
  });
  it('T40.29 should change map to style 2', () => {
    let styleSpy = spyOn(component, 'mapStyle2').and.callThrough();
    component.mapStyle2();
    expect(styleSpy).toHaveBeenCalled();
  });
  it('T40.30 should change map to style 3', () => {
    let styleSpy = spyOn(component, 'mapStyle3').and.callThrough();
    component.mapStyle3();
    expect(styleSpy).toHaveBeenCalled();
  });
  it('T40.31 should change map to style 4', () => {
    let styleSpy = spyOn(component, 'mapStyle4').and.callThrough();
    component.mapStyle4();
    expect(styleSpy).toHaveBeenCalled();
  });
});
