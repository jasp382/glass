import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { FeatModule } from 'src/app/feat/feat.module';
import { SentinelImg } from 'src/app/interfaces/geospatial';

import { SatelliteComponent } from './satellite.component';

describe('TS14 Backoffice SatelliteComponent', () => {
  let component: SatelliteComponent;
  let fixture: ComponentFixture<SatelliteComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SatelliteComponent],
      imports: [
        HttpClientTestingModule,
        FeatModule,
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(SatelliteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T14.1 should create', () => { expect(component).toBeTruthy(); });

  it('T14.2 should get datasets from API', () => {
    // setup
    let getSpy = spyOn(component, 'getDatasets').and.callThrough();
    let getAPISpy = spyOn(component['satServ'], 'getSatDatasets')
      .and.returnValue(of({
        data: [{
          id: 1, identifier: '', datastripidentifier: '', granuleidentifier: '', level1cpdiidentifier: '',
          platformidentifier: '', platformserialidentifier: '', s2datatakeid: '', uuid: '', title: '',
          summary: '', beginposition: '', endposition: '', ingestiondate: '', generationdate: '',
          cloudcoverpercentage: '', mediumprobacloudspercentage: '', highprobacloudspercentage: '',
          vegetationpercentage: '', notvegetatedpercentage: '', waterpercentage: '', unclassifiedpercentage: '',
          snowicepercentage: '', orbitnumber: 1, relativeorbitnumber: 1, orbitdirection: '', geometry: '',
          illuminationazimuthangle: 1, illuminationzenithangle: 1, processingbaseline: '', processinglevel: '',
          ondemand: '', isdownload: false, filename: '', link: '', format: '', platformname: '', instrumentname: '',
          instrumentshortname: '', size: '', producttype: ''
        }]
      }));
    let dataSpy = spyOn(component, 'getDatasetData').and.callThrough();
    let processSpy = spyOn(component, 'processDate');
    let rowSpy = spyOn(component, 'updateRowCount');

    component.getDatasets();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).toHaveBeenCalled();
    expect(processSpy).toHaveBeenCalledTimes(4);
    expect(rowSpy).toHaveBeenCalled();
  });

  it('T14.3 should handle error from getting datasets from API', () => {
    // setup
    let getSpy = spyOn(component, 'getDatasets').and.callThrough();
    let getAPISpy = spyOn(component['satServ'], 'getSatDatasets')
      .and.returnValue(throwError(() => new Error()));
    let dataSpy = spyOn(component, 'getDatasetData').and.callThrough();
    let processSpy = spyOn(component, 'processDate');
    let rowSpy = spyOn(component, 'updateRowCount');

    component.getDatasets();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).not.toHaveBeenCalled();
    expect(processSpy).not.toHaveBeenCalled();
    expect(rowSpy).not.toHaveBeenCalled();
  });

  it('T14.4 should format date from API request', () => {
    // setup
    let formatSpy = spyOn(component, 'processDate').and.callThrough();
    let result = component.processDate('2009-06-15T13:45:30');
    expect(formatSpy).toHaveBeenCalled();
    expect(result).toEqual('15/06/2009 13:45:30');
  });

  it('T14.5 should update search terms', () => {
    // spies
    let searchSpy = spyOn(component, 'searchDatasets').and.callThrough();

    component.searchDatasets(null as unknown as string);
    component.searchDatasets('search');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('search');
    expect(component.searchTerms).toEqual('search');
  });

  it('T14.6 should get current page for table component', () => {
    // setup
    let pageSpy = spyOn(component, 'getPage').and.callThrough();

    component.getPage(5);

    // expectations
    expect(pageSpy).toHaveBeenCalledOnceWith(5);
    expect(component.currentPage).toBe(5);
  });

  it('T14.7 should update data row count for pagination', () => {
    // setup
    let rowSpy = spyOn(component, 'updateRowCount').and.callThrough();

    component.updateRowCount(10);

    // expectations
    expect(rowSpy).toHaveBeenCalledOnceWith(10);
    expect(component.rowCount).toBe(10);
  });

  it('T14.8 should open dataset details view', () => {
    // fake data
    let datasets: SentinelImg[] = [
      {
        id: 1,
        identifier: '', dataStripIdentifier: '', granuleIdentifier: '', level1CpdiIdentifier: '', platformIdentifier: '',
        platformSerialIdentifier: '', s2DataTakeId: '', uuid: '', title: '', summary: '', beginPositionDate: '', endPositionDate: '',
        ingestionDate: '', generationDate: '', cloudCoverPercentage: '', mediumProbCloudsPercentage: '', highProbCloudsPercentage: '',
        vegetationPercentage: '', notVegetatedPercentage: '', waterPercentage: '', unclassifiedPercentage: '', snowIcePercentage: '',
        orbitNumber: 1, relativeOrbitNumber: 1, orbitDirection: '', geometry: '', illuminationAzimuthAngle: 1, illuminationZenithAngle: 1,
        processingBaseline: '', processingLevel: '', onDemand: '', isDownload: false, fileName: '', link: '', format: '', platformName: '',
        instrumentName: '', instrumentShortName: '', size: '', productType: '',
      },
    ];
    component.datasets = datasets;
    fixture.detectChanges();

    // spies
    let datasetViewSpy = spyOn(component, 'toggleDatasetView').and.callThrough();

    component.toggleDatasetView(1);

    // expectations
    expect(datasetViewSpy).toHaveBeenCalledWith(1);
    expect(component.isDatasetOpen).toBeTrue();
    expect(component.displayedHeaders).toEqual(component.openHeaders);
    expect(component.openDataset).toEqual(datasets[0]);
  });

  it('T14.9 should close dataset details view', () => {
    // fake data
    let datasets: SentinelImg[] = [
      {
        id: 1,
        identifier: '', dataStripIdentifier: '', granuleIdentifier: '', level1CpdiIdentifier: '', platformIdentifier: '',
        platformSerialIdentifier: '', s2DataTakeId: '', uuid: '', title: '', summary: '', beginPositionDate: '', endPositionDate: '',
        ingestionDate: '', generationDate: '', cloudCoverPercentage: '', mediumProbCloudsPercentage: '', highProbCloudsPercentage: '',
        vegetationPercentage: '', notVegetatedPercentage: '', waterPercentage: '', unclassifiedPercentage: '', snowIcePercentage: '',
        orbitNumber: 1, relativeOrbitNumber: 1, orbitDirection: '', geometry: '', illuminationAzimuthAngle: 1, illuminationZenithAngle: 1,
        processingBaseline: '', processingLevel: '', onDemand: '', isDownload: false, fileName: '', link: '', format: '', platformName: '',
        instrumentName: '', instrumentShortName: '', size: '', productType: '',
      },
    ];
    component.datasets = datasets;
    fixture.detectChanges();

    // spies
    let datasetViewSpy = spyOn(component, 'toggleDatasetView').and.callThrough();

    component.toggleDatasetView(-1);

    // expectations
    expect(datasetViewSpy).toHaveBeenCalledWith(-1);
    expect(component.isDatasetOpen).toBeFalse();
    expect(component.displayedHeaders).toEqual(component.headers);
    expect(component.isDetOpen).toBeFalse();
    expect(component.isIDsOpen).toBeFalse();
    expect(component.isDatesOpen).toBeFalse();
    expect(component.isPercentOpen).toBeFalse();
    expect(component.isGeoOpen).toBeFalse();
    expect(component.isProcOpen).toBeFalse();
    expect(component.isOtherOpen).toBeFalse();
  });

  describe('TS14.1 should toggle info dropdowns', () => {
    it('T14.1.1 toggle details', () => {
      let toggleSpy = spyOn(component, 'toggleInfoDropdown').and.callThrough();
      expect(component.isDetOpen).toBeFalse();
      component.toggleInfoDropdown('details');
      expect(component.isDetOpen).toBeTrue();
      expect(toggleSpy).toHaveBeenCalled();
    });
    it('T14.1.2 toggle ids', () => {
      let toggleSpy = spyOn(component, 'toggleInfoDropdown').and.callThrough();
      expect(component.isIDsOpen).toBeFalse();
      component.toggleInfoDropdown('ids');
      expect(component.isIDsOpen).toBeTrue();
      expect(toggleSpy).toHaveBeenCalled();
    });
    it('T14.1.3 toggle dates', () => {
      let toggleSpy = spyOn(component, 'toggleInfoDropdown').and.callThrough();
      expect(component.isDatesOpen).toBeFalse();
      component.toggleInfoDropdown('dates');
      expect(component.isDatesOpen).toBeTrue();
      expect(toggleSpy).toHaveBeenCalled();
    });
    it('T14.1.4 toggle percent', () => {
      let toggleSpy = spyOn(component, 'toggleInfoDropdown').and.callThrough();
      expect(component.isPercentOpen).toBeFalse();
      component.toggleInfoDropdown('percent');
      expect(component.isPercentOpen).toBeTrue();
      expect(toggleSpy).toHaveBeenCalled();
    });
    it('T14.1.5 toggle geo', () => {
      let toggleSpy = spyOn(component, 'toggleInfoDropdown').and.callThrough();
      expect(component.isGeoOpen).toBeFalse();
      component.toggleInfoDropdown('geo');
      expect(component.isGeoOpen).toBeTrue();
      expect(toggleSpy).toHaveBeenCalled();
    });
    it('T14.1.6 toggle proc', () => {
      let toggleSpy = spyOn(component, 'toggleInfoDropdown').and.callThrough();
      expect(component.isProcOpen).toBeFalse();
      component.toggleInfoDropdown('proc');
      expect(component.isProcOpen).toBeTrue();
      expect(toggleSpy).toHaveBeenCalled();
    });
    it('T14.1.7 toggle other', () => {
      let toggleSpy = spyOn(component, 'toggleInfoDropdown').and.callThrough();
      expect(component.isOtherOpen).toBeFalse();
      component.toggleInfoDropdown('other');
      expect(component.isOtherOpen).toBeTrue();
      expect(toggleSpy).toHaveBeenCalled();
    });
  });

  it('T14.10 should open modal to delete dataset', () => {
    // spies
    let openModalSpy = spyOn(component, 'openDeleteModal').and.callThrough();
    let openSpy = spyOn(component['modalService'], 'open');

    component.openDeleteModal({});

    // expectations
    expect(openModalSpy).toHaveBeenCalled();
    expect(component.isConfChecked).toBeFalse();
    expect(component.hasClickedRemove).toBeFalse();
    expect(openSpy).toHaveBeenCalled();
  });

  it('T14.11 it should remove a dataset', () => {
    // fake data
    let datasets: SentinelImg[] = [
      {
        id: 1,
        identifier: '', dataStripIdentifier: '', granuleIdentifier: '', level1CpdiIdentifier: '', platformIdentifier: '',
        platformSerialIdentifier: '', s2DataTakeId: '', uuid: '', title: '', summary: '', beginPositionDate: '', endPositionDate: '',
        ingestionDate: '', generationDate: '', cloudCoverPercentage: '', mediumProbCloudsPercentage: '', highProbCloudsPercentage: '',
        vegetationPercentage: '', notVegetatedPercentage: '', waterPercentage: '', unclassifiedPercentage: '', snowIcePercentage: '',
        orbitNumber: 1, relativeOrbitNumber: 1, orbitDirection: '', geometry: '', illuminationAzimuthAngle: 1, illuminationZenithAngle: 1,
        processingBaseline: '', processingLevel: '', onDemand: '', isDownload: false, fileName: '', link: '', format: '', platformName: '',
        instrumentName: '', instrumentShortName: '', size: '', productType: '',
      },
    ];
    component.datasets = datasets;
    component.openDataset = datasets[0];
    component.isConfChecked = true;
    fixture.detectChanges();
    // spies
    let removeSpy = spyOn(component, 'removeDataset').and.callThrough();
    let removeAPISpy = spyOn(component['satServ'], 'deleteSatDataset').and.returnValue(of({}));
    let rowSpy = spyOn(component, 'updateRowCount');

    component.removeDataset();

    // expectations
    expect(removeSpy).toHaveBeenCalled();
    expect(removeAPISpy).toHaveBeenCalled();
    expect(component.isDatasetOpen).toBeFalse();
    expect(component.displayedHeaders).toEqual(component.headers);
    expect(component.datasets.length).toBe(0);
    expect(rowSpy).toHaveBeenCalled();
  });

  it('T14.12 it should handle error from removing a dataset', () => {
    // fake data
    let datasets: SentinelImg[] = [
      {
        id: 1,
        identifier: '', dataStripIdentifier: '', granuleIdentifier: '', level1CpdiIdentifier: '', platformIdentifier: '',
        platformSerialIdentifier: '', s2DataTakeId: '', uuid: '', title: '', summary: '', beginPositionDate: '', endPositionDate: '',
        ingestionDate: '', generationDate: '', cloudCoverPercentage: '', mediumProbCloudsPercentage: '', highProbCloudsPercentage: '',
        vegetationPercentage: '', notVegetatedPercentage: '', waterPercentage: '', unclassifiedPercentage: '', snowIcePercentage: '',
        orbitNumber: 1, relativeOrbitNumber: 1, orbitDirection: '', geometry: '', illuminationAzimuthAngle: 1, illuminationZenithAngle: 1,
        processingBaseline: '', processingLevel: '', onDemand: '', isDownload: false, fileName: '', link: '', format: '', platformName: '',
        instrumentName: '', instrumentShortName: '', size: '', productType: '',
      },
    ];
    component.datasets = datasets;
    component.openDataset = datasets[0];
    component.isConfChecked = true;
    fixture.detectChanges();
    // spies
    let removeSpy = spyOn(component, 'removeDataset').and.callThrough();
    let removeAPISpy = spyOn(component['satServ'], 'deleteSatDataset').and.returnValue(throwError(() => new Error()));
    let rowSpy = spyOn(component, 'updateRowCount');

    component.removeDataset();

    // expectations
    expect(removeSpy).toHaveBeenCalled();
    expect(removeAPISpy).toHaveBeenCalled();
    expect(component.datasets.length).not.toBe(0);
    expect(rowSpy).not.toHaveBeenCalled();
  });

  it('T14.13 it should not remove a dataset without confirmation', () => {
    // fake data
    let datasets: SentinelImg[] = [
      {
        id: 1,
        identifier: '', dataStripIdentifier: '', granuleIdentifier: '', level1CpdiIdentifier: '', platformIdentifier: '',
        platformSerialIdentifier: '', s2DataTakeId: '', uuid: '', title: '', summary: '', beginPositionDate: '', endPositionDate: '',
        ingestionDate: '', generationDate: '', cloudCoverPercentage: '', mediumProbCloudsPercentage: '', highProbCloudsPercentage: '',
        vegetationPercentage: '', notVegetatedPercentage: '', waterPercentage: '', unclassifiedPercentage: '', snowIcePercentage: '',
        orbitNumber: 1, relativeOrbitNumber: 1, orbitDirection: '', geometry: '', illuminationAzimuthAngle: 1, illuminationZenithAngle: 1,
        processingBaseline: '', processingLevel: '', onDemand: '', isDownload: false, fileName: '', link: '', format: '', platformName: '',
        instrumentName: '', instrumentShortName: '', size: '', productType: '',
      },
    ];
    component.datasets = datasets;
    component.openDataset = datasets[0];
    fixture.detectChanges();
    // spies
    let removeSpy = spyOn(component, 'removeDataset').and.callThrough();
    let removeAPISpy = spyOn(component['satServ'], 'deleteSatDataset').and.returnValue(of({}));
    let rowSpy = spyOn(component, 'updateRowCount');

    component.removeDataset();

    // expectations
    expect(removeSpy).toHaveBeenCalled();
    expect(removeAPISpy).not.toHaveBeenCalled();
    expect(component.datasets.length).not.toBe(0);
    expect(rowSpy).not.toHaveBeenCalled();
  });
});
