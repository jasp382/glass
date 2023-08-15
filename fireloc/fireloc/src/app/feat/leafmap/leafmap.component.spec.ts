import { Component } from '@angular/core';
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { Extent } from 'src/app/constants/mapext';
import { MapSettings } from 'src/app/interfaces/maps';

import { LeafmapComponent } from './leafmap.component';

// Mock Host Component
@Component({
  selector: 'test-host',
  template: `
  <app-leafmap 
    [map-settings]="mapSettings"
  ></app-leafmap>`,
  styles: [':host { width: 300px }'],
})
class TestHostComponent {
  mapSettings!: MapSettings;
}

describe('TS30 LeafmapComponent', () => {
  // map component
  let mapComponent: LeafmapComponent;

  // fake host
  let hostComponent: TestHostComponent;
  let hostFixture: ComponentFixture<TestHostComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [LeafmapComponent, TestHostComponent]
    }).compileComponents();

    // fake host component
    hostFixture = TestBed.createComponent(TestHostComponent);
    hostComponent = hostFixture.componentInstance;

    // map component
    mapComponent = hostFixture.debugElement.query(By.directive(LeafmapComponent)).componentInstance;

    // defaults
    hostComponent.mapSettings = {
      domElem: 'fake-test-elem',
      mapContainer: 'fakeTestContainer',
      minZoom: 0,
      maxZoom: 0,
      scale: false,
      zoomCtrl: false,
      bounds: Extent.bounds,
      fullext: Extent.maxBounds,
      wfs: [],
      wms: []
    };

    hostFixture.detectChanges();
  });

  it('T30.1 should create host component', () => { expect(hostComponent).toBeTruthy(); });

  it('T30.2 should create map component', () => { expect(mapComponent).toBeTruthy(); });

  it('T30.3 should check if map exists before invalidating size', () => {
    let invalidateSpy = spyOn(mapComponent['map'], 'invalidateSize');
    mapComponent.map = undefined;
    mapComponent.ngOnInit();
    expect(invalidateSpy).not.toHaveBeenCalled();
  });

  it('T30.4 should invalidate map size if map exists', () => {
    let invalidateSpy = spyOn(mapComponent['map'], 'invalidateSize');
    mapComponent.ngOnInit();
    expect(invalidateSpy).toHaveBeenCalled();
  });

  it('T30.5 should check if map exists before creating a new map (not create a map)', () => {
    let createSpy = spyOn(mapComponent['mapServ'], 'createMap');
    let updateSpy = spyOn(mapComponent['lyrServ'], 'updateBasemap');
    let emitterSpy = spyOn(mapComponent['mapEmitter'], 'emit');

    mapComponent['mapResizeObserver'].disconnect();
    mapComponent.ngAfterViewInit();

    expect(createSpy).not.toHaveBeenCalled();
    expect(updateSpy).not.toHaveBeenCalled();
    expect(emitterSpy).not.toHaveBeenCalled();
  });

  it('T30.6 should check if map exists before creating a new map (create a new map)', () => {
    let createSpy = spyOn(mapComponent['mapServ'], 'createMap');
    let updateSpy = spyOn(mapComponent['lyrServ'], 'updateBasemap');
    let emitterSpy = spyOn(mapComponent['mapEmitter'], 'emit');
    spyOn(document, 'getElementById').and.returnValue(null);
    spyOn(mapComponent['map'], 'invalidateSize');

    mapComponent.map = undefined;
    mapComponent.ngAfterViewInit();

    expect(createSpy).toHaveBeenCalled();
    expect(updateSpy).toHaveBeenCalled();
    expect(emitterSpy).toHaveBeenCalled();
  });

  it('T30.7 should resize map', () => {
    let resizeSpy = spyOn(mapComponent, 'resized').and.callThrough();
    let invalidateSpy = spyOn(mapComponent['map'], 'invalidateSize');
    let changeSpy = spyOn(mapComponent['changeDetector'], 'detectChanges');

    mapComponent.resized();
    expect(resizeSpy).toHaveBeenCalled();
    expect(invalidateSpy).toHaveBeenCalled();
    expect(changeSpy).toHaveBeenCalled();
  });

  it('T30.8 should not resize map if there is no map', () => {
    let resizeSpy = spyOn(mapComponent, 'resized').and.callThrough();
    let invalidateSpy = spyOn(mapComponent['map'], 'invalidateSize');
    let changeSpy = spyOn(mapComponent['changeDetector'], 'detectChanges');
    mapComponent.map = null;

    mapComponent.resized();
    expect(resizeSpy).toHaveBeenCalled();
    expect(invalidateSpy).not.toHaveBeenCalled();
    expect(changeSpy).not.toHaveBeenCalled();
  });

  it('T30.9 resized function is called when element is resized', waitForAsync(() => {
    spyOn(mapComponent['map'], 'invalidateSize');
    spyOn(mapComponent['changeDetector'], 'detectChanges');

    const resizeTestComponentDebugElement = hostFixture.debugElement.query(
      By.directive(LeafmapComponent)
    );
    const resizedSpy = spyOn(
      resizeTestComponentDebugElement.componentInstance, 'resized'
    );

    resizedSpy.and.callThrough();
    hostFixture.detectChanges();
    setTimeout(() => { // process first resize when component is first drawn
      hostFixture.whenStable().then(() => {
        hostFixture.debugElement.nativeElement.style.width = '200px';
        hostFixture.detectChanges();
        setTimeout(() => { // process resize due to width change.
          hostFixture.whenStable().then(() => {
            expect(resizedSpy).toHaveBeenCalled();
          });
        }, 0);
      });
    }, 0);
  }));

});
