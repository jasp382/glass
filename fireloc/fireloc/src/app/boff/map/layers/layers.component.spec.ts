import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { of, throwError } from 'rxjs';
import { FeatModule } from 'src/app/feat/feat.module';
import { FirelocLayer } from 'src/app/interfaces/layers';

import { LayersComponent } from './layers.component';

describe('TS18 Backoffice LayersComponent', () => {
  let component: LayersComponent;
  let fixture: ComponentFixture<LayersComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [LayersComponent],
      imports: [
        HttpClientTestingModule,
        FeatModule,
        FontAwesomeModule,
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(LayersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('T18.1 should create', () => { expect(component).toBeTruthy(); });

  it('T18.2 should get layers from API', () => {
    // setup
    let getSpy = spyOn(component, 'getLayers').and.callThrough();
    let getAPISpy = spyOn(component['layerServ'], 'getLayersToken')
      .and.returnValue(of({
        data: [{
          id: 1, slug: 'slug', level: 1, rootid: 1, designation: '', gsrvlyr: '', store: '', style: '',
          workspace: '', child: [{
            id: 2, slug: 'slug', level: 2, rootid: 1, designation: '', gsrvlyr: '', store: '', style: '',
            workspace: '', child: [{
              id: 3, slug: 'slug', level: 3, rootid: 2, designation: '', gsrvlyr: '', store: '', style: '',
              workspace: '', child: null
            }],
          }],
        },
        ]
      }));
    let dataSpy = spyOn(component, 'getLayersInformation').and.callThrough();
    let childrenSpy = spyOn(component, 'getLayerChildren').and.callThrough();

    component.getLayers();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).toHaveBeenCalled();
    expect(childrenSpy).toHaveBeenCalled();
    expect(component.layers.length).not.toBe(0);
  });

  it('T18.3 should handle error from getting charts from API', () => {
    // setup
    let getSpy = spyOn(component, 'getLayers').and.callThrough();
    let getAPISpy = spyOn(component['layerServ'], 'getLayersToken').and.returnValue(throwError(() => new Error()));
    let dataSpy = spyOn(component, 'getLayersInformation').and.callThrough();
    let childrenSpy = spyOn(component, 'getLayerChildren').and.callThrough();

    component.getLayers();

    // expectations
    expect(getSpy).toHaveBeenCalled();
    expect(getAPISpy).toHaveBeenCalled();
    expect(dataSpy).not.toHaveBeenCalled();
    expect(childrenSpy).not.toHaveBeenCalled();
    expect(component.layers.length).toBe(0);
  });

  it('T18.4 should filter layers by name', () => {
    // fake data
    let layers: FirelocLayer[] = [{
      id: 1, slug: '', level: 1, rootID: 1, designation: '', serverLayer: '',
      store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
    }];
    component.layers = layers;
    fixture.detectChanges();

    // spies
    let searchSpy = spyOn(component, 'searchLayers').and.callThrough();
    let recursiveSpy = spyOn(component, 'recursiveFilter');

    component.searchLayers(null as unknown as string);
    component.searchLayers('');
    component.searchLayers('name');

    // expectations
    expect(searchSpy).toHaveBeenCalledWith('');
    expect(searchSpy).toHaveBeenCalledWith('name');
    expect(recursiveSpy).toHaveBeenCalled();
  });

  it('T18.5 should recursively search for layers by name', () => {
    // fake data
    let layers: any[] = [
      {
        designation: '', child: [{
          designation: 'nope', child: null
        },
        {
          designation: '', child: [{
            designation: 'name', child: null
          }],
        }]
      },
      {
        designation: 'nope', child: [{
          designation: 'nope', child: null
        },
        {
          designation: '', child: [{
            designation: null, child: null
          }],
        }]
      },
    ];

    let recursiveSpy = spyOn(component, 'recursiveFilter').and.callThrough();
    let result = component.recursiveFilter(layers, 'name');

    // expectations
    expect(recursiveSpy).toHaveBeenCalled();
    expect(result).toEqual([layers[0]]);
  });

  it('T18.6 should open category', () => {
    // fake data
    let layers: FirelocLayer[] = [{
      id: 1,
      slug: '', level: 1, rootID: 1, designation: '', serverLayer: '',
      store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
        [{
          id: 2,
          slug: '', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
          store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
        },
        {
          id: 3,
          slug: '', level: 2, rootID: 1, designation: '', serverLayer: '',
          store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
            [{
              id: 4,
              slug: '', level: 3, rootID: 3, designation: 'name', serverLayer: '',
              store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
            }],
        },
        ]
    }];
    component.layers = layers;
    component.filteredLayers = layers;
    fixture.detectChanges();

    let toggleSpy = spyOn(component, 'toggleCategory').and.callThrough();
    component.toggleCategory(1, { path: [{}, { id: 'editIcon' }] });
    component.toggleCategory(1, { path: [{}, { id: '' }, { id: 'editIcon' }] });
    component.toggleCategory(1, { path: [{}, { id: '' }, { id: '' }] });

    // expectations
    expect(toggleSpy).toHaveBeenCalled();
    expect(component.layers[0].isOpen).toBeTrue();
  });

  it('T18.7 should close category', () => {
    // fake data
    let layers: FirelocLayer[] = [{
      id: 1,
      slug: '', level: 1, rootID: 1, designation: '', serverLayer: '',
      store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
        [{
          id: 2,
          slug: '', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
          store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
        },
        {
          id: 3,
          slug: '', level: 2, rootID: 1, designation: '', serverLayer: '',
          store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
            [{
              id: 4,
              slug: '', level: 3, rootID: 3, designation: 'name', serverLayer: '',
              store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
            }],
        },
        ]
    }];
    component.layers = layers;
    component.filteredLayers = layers;
    fixture.detectChanges();

    let toggleSpy = spyOn(component, 'toggleCategory').and.callThrough();
    component.toggleCategory(1, { path: [{}, { id: 'editIcon' }] });
    component.toggleCategory(1, { path: [{}, { id: '' }, { id: 'editIcon' }] });
    component.toggleCategory(1, { path: [{}, { id: '' }, { id: '' }] });

    // expectations
    expect(toggleSpy).toHaveBeenCalled();
    expect(component.layers[0].isOpen).toBeFalse();
  });

  it('T18.8 should open create modal for new layer', () => {
    // fake data
    let layers: FirelocLayer[] = [{
      id: 1,
      slug: '', level: 1, rootID: 1, designation: '', serverLayer: '',
      store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
        [{
          id: 2,
          slug: '', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
          store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
        },
        {
          id: 3,
          slug: '', level: 2, rootID: 1, designation: '', serverLayer: '',
          store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
            [{
              id: 4,
              slug: '', level: 3, rootID: 3, designation: 'name', serverLayer: '',
              store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
            }],
        },
        ]
    }];
    component.layers = layers;
    fixture.detectChanges();

    let openSpy = spyOn(component, 'openCreateModal').and.callThrough();
    let modalSpy = spyOn(component['modalService'], 'open');
    component.openCreateModal({});

    expect(openSpy).toHaveBeenCalled();
    expect(component.newLayer.category).toEqual(layers[0]);
    expect(component.newCategory.parent).toEqual(layers[0]);
    expect(modalSpy).toHaveBeenCalled();
  });

  it('T18.9 should update new category property when form changes', () => {
    // spies
    let updateSpy = spyOn(component, 'updateNewCategoryField').and.callThrough();

    component.updateNewCategoryField('design', 'layerDesignaton');

    // expectations
    expect(updateSpy).toHaveBeenCalledWith('design', 'layerDesignaton');
    expect(component.newCategory.layerDesignaton).toEqual('design');
  });

  it('T18.10 should update new layer property when form changes', () => {
    // spies
    let updateSpy = spyOn(component, 'updateNewLayerField').and.callThrough();

    component.updateNewLayerField('design', 'designation');

    // expectations
    expect(updateSpy).toHaveBeenCalledWith('design', 'designation');
    expect(component.newLayer.designation).toEqual('design');
  });

  it('T18.11 should find layer and add child', () => {
    // spies
    let addSpy = spyOn(component, 'findLayerAndAddChild').and.callThrough();

    let layer = { id: 1, child: null };
    let parent = { id: 1 };
    let child = {};
    component.findLayerAndAddChild(layer, parent, child);

    let layer2 = { id: 1, child: [] };
    let parent2 = { id: 1 };
    let child2 = { id: 3, child: null };
    component.findLayerAndAddChild(layer2, parent2, child2);

    let layer3 = { id: 1, child: [{ id: 2, child: [] }] };
    let parent3 = { id: 2 };
    let child3 = { id: 3, child: null };
    component.findLayerAndAddChild(layer3, parent3, child3);

    expect(addSpy).toHaveBeenCalledTimes(4);
    expect(layer2.child.length).toBe(1);
    expect(layer3.child[0].child.length).toBe(1);

  });

  describe('TS18.1 create a new category', () => {
    it('T18.1.1 should not create a new category if new category form is invalid', () => {
      // spies
      let createSpy = spyOn(component, 'createCategory').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer');

      component.createCategory();

      // expectations
      expect(createSpy).toHaveBeenCalled();
      expect(addAPISpy).not.toHaveBeenCalled();
    });

    it('T18.1.2 should create a new category (without parent)', () => {
      // spies
      let createSpy = spyOn(component, 'createCategory').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake new information
      component.newCategoryForm.patchValue({
        hasParent: false, catDesignation: 'designation', catSlug: 'slug', layerDesignation: 'design', layerSlug: 'slug',
        layerWorkspace: 'work', layerStore: 'store', layerServerLayer: 'server', layerStyle: 'style'
      });
      fixture.detectChanges();

      component.createCategory();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      expect(component.layers.length).not.toBe(0);
    });

    it('T18.1.3 should create a new category (with parent - first level)', () => {
      // spies
      let createSpy = spyOn(component, 'createCategory').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.newCategory.hasParent = true;
      component.newCategory.parent = layers[0];

      // fake new information
      component.newCategoryForm.patchValue({
        hasParent: true, parentCategory: layers[0], catDesignation: 'designation', catSlug: 'slug',
        layerDesignation: 'design', layerSlug: 'slug', layerWorkspace: 'work', layerStore: 'store',
        layerServerLayer: 'server', layerStyle: 'style'
      });
      fixture.detectChanges();

      component.createCategory();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      if (component.layers[0].child) expect(component.layers[0].child.length).not.toBe(2);
    });

    it('T18.1.4 should create a new category (with parent - not first level)', () => {
      // spies
      let createSpy = spyOn(component, 'createCategory').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.newCategory.hasParent = true;
      component.newCategory.parent = layers[0].child ? layers[0].child[1] : null;

      // fake new information
      component.newCategoryForm.patchValue({
        hasParent: true, parentCategory: layers[0].child ? layers[0].child[1] : null, catDesignation: 'designation',
        catSlug: 'slug', layerDesignation: 'design', layerSlug: 'slug', layerWorkspace: 'work', layerStore: 'store',
        layerServerLayer: 'server', layerStyle: 'style'
      });
      fixture.detectChanges();

      component.createCategory();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      if (component.layers[0].child && component.layers[0].child[1].child)
        expect(component.layers[0].child[1].child.length).not.toBe(1);
    });

    it('T18.1.5 should handle error from creating a new category', () => {
      // spies
      let createSpy = spyOn(component, 'createCategory').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer').and.returnValue(throwError(() => new Error()));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.newCategory.hasParent = true;
      component.newCategory.parent = layers[0].child ? layers[0].child[1] : null;

      // fake new information
      component.newCategoryForm.patchValue({
        hasParent: true, parentCategory: layers[0].child ? layers[0].child[1] : null, catDesignation: 'designation',
        catSlug: 'slug', layerDesignation: 'design', layerSlug: 'slug', layerWorkspace: 'work', layerStore: 'store',
        layerServerLayer: 'server', layerStyle: 'style'
      });
      fixture.detectChanges();

      component.createCategory();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      if (component.layers[0].child && component.layers[0].child[1].child)
        expect(component.layers[0].child[1].child.length).toBe(1);
    });

    it('T18.1.6 should not add category if parent is not meant to have children', () => {
      // spies
      let createSpy = spyOn(component, 'createCategory').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }, {
        id: 5,
        slug: 'slug5', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child: null
      }
      ];
      component.layers = layers;
      component.newCategory.hasParent = true;
      component.newCategory.parent = layers[1];

      // fake new information
      component.newCategoryForm.patchValue({
        hasParent: true, parentCategory: layers[1], catDesignation: 'designation',
        catSlug: 'slug', layerDesignation: 'design', layerSlug: 'slug', layerWorkspace: 'work', layerStore: 'store',
        layerServerLayer: 'server', layerStyle: 'style'
      });
      fixture.detectChanges();

      component.createCategory();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      expect(component.layers[1].child).toBeNull();
    });
  });

  describe('TS18.2 create a new layer', () => {
    it('T18.2.1 should not create a new layer if new layer form is invalid', () => {
      // spies
      let createSpy = spyOn(component, 'createLayer').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer');

      component.createLayer();

      // expectations
      expect(createSpy).toHaveBeenCalled();
      expect(addAPISpy).not.toHaveBeenCalled();
    });

    it('T18.2.2 should create a new layer (with parent - first level)', () => {
      // spies
      let createSpy = spyOn(component, 'createLayer').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.newLayer.category = layers[0];

      // fake new information
      component.newLayerForm.patchValue({
        category: layers[0], designation: 'design', slug: 'slug', workspace: 'work',
        store: 'store', serverLayer: 'server', style: 'style'
      });
      fixture.detectChanges();

      component.createLayer();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      if (component.layers[0].child) expect(component.layers[0].child.length).not.toBe(2);
    });

    it('T18.2.3 should create a new layer (with parent - not first level)', () => {
      // spies
      let createSpy = spyOn(component, 'createLayer').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.newLayer.category = layers[0].child ? layers[0].child[1] : null;

      // fake new information
      component.newLayerForm.patchValue({
        category: layers[0].child ? layers[0].child[1] : null, designation: 'design', slug: 'slug',
        workspace: 'work', store: 'store', serverLayer: 'server', style: 'style'
      });
      fixture.detectChanges();

      component.createLayer();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      if (component.layers[0].child && component.layers[0].child[1].child)
        expect(component.layers[0].child[1].child.length).not.toBe(1);
    });

    it('T18.2.4 should handle error from creating a new layer', () => {
      // spies
      let createSpy = spyOn(component, 'createLayer').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer').and.returnValue(throwError(() => new Error()));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.newLayer.category = layers[0].child ? layers[0].child[1] : null;

      // fake new information
      component.newLayerForm.patchValue({
        category: layers[0].child ? layers[0].child[1] : null, designation: 'design', slug: 'slug',
        workspace: 'work', store: 'store', serverLayer: 'server', style: 'style'
      });
      fixture.detectChanges();

      component.createLayer();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      if (component.layers[0].child && component.layers[0].child[1].child)
        expect(component.layers[0].child[1].child.length).toBe(1);
    });

    it('T18.2.5 should not add layer if parent is not meant to have children', () => {
      // spies
      let createSpy = spyOn(component, 'createLayer').and.callThrough();
      let addAPISpy = spyOn(component['layerServ'], 'createLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }, {
        id: 5,
        slug: 'slug5', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child: null
      }
      ];
      component.layers = layers;
      component.newLayer.category = layers[1];

      // fake new information
      component.newLayerForm.patchValue({
        category: layers[1], designation: 'design', slug: 'slug',
        workspace: 'work', store: 'store', serverLayer: 'server', style: 'style'
      });
      fixture.detectChanges();

      component.createLayer();

      // expectations
      expect(createSpy).toHaveBeenCalledWith();
      expect(addAPISpy).toHaveBeenCalled();
      expect(component.layers[1].child).toBeNull();
    });
  });

  describe('TS18.3 update a category', () => {
    it('T18.3.1 should open edit modal to update a category', () => {
      // setup
      let openSpy = spyOn(component, 'openEditModal').and.callThrough();
      let modalSpy = spyOn(component['modalService'], 'open');
      let category: FirelocLayer = {
        id: 0, designation: '', serverLayer: '', slug: 'slug',
        store: '', style: '', workspace: '', child: []
      };

      component.openEditModal(category, {});

      expect(openSpy).toHaveBeenCalled();
      expect(component.openLayer).toEqual(category);
      expect(component.openLayerSlug).toEqual('slug');
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T18.3.2 should not update a category if edit category form is invalid', () => {
      // spies
      let updateSpy = spyOn(component, 'updateCategory').and.callThrough();
      let updateAPISpy = spyOn(component['layerServ'], 'updateLayer');

      component.updateCategory();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).not.toHaveBeenCalled();
    });

    it('T18.3.3 should update a category (update all fields)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateCategory').and.callThrough();
      let updateAPISpy = spyOn(component['layerServ'], 'updateLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.openLayer = layers[0];

      // fake edit information
      component.editCategoryForm.patchValue({ designation: 'design', slug: 'slug' });
      component.editCategoryForm.get('designation')?.markAsDirty();
      component.editCategoryForm.get('slug')?.markAsDirty();
      fixture.detectChanges();

      component.updateCategory();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).toHaveBeenCalled();
    });

    it('T18.3.4 should update a category (update one field)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateCategory').and.callThrough();
      let updateAPISpy = spyOn(component['layerServ'], 'updateLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.openLayer = layers[0];

      // fake edit information
      component.editCategoryForm.patchValue({ designation: 'design', slug: 'slug' });
      component.editCategoryForm.get('designation')?.markAsDirty();
      fixture.detectChanges();

      component.updateCategory();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).toHaveBeenCalled();
    });

    it('T18.3.5 should handle error from updating a category', () => {
      // spies
      let updateSpy = spyOn(component, 'updateCategory').and.callThrough();
      let updateAPISpy = spyOn(component['layerServ'], 'updateLayer').and.returnValue(throwError(() => new Error()));
      let findUpdateSpy = spyOn(component, 'findLayerAndUpdate');

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.openLayer = layers[0];

      // fake edit information
      component.editCategoryForm.patchValue({ designation: 'design', slug: 'slug' });
      component.editCategoryForm.get('designation')?.markAsDirty();
      fixture.detectChanges();

      component.updateCategory();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).toHaveBeenCalled();
      expect(findUpdateSpy).not.toHaveBeenCalled();
    });
  });

  describe('TS18.4 update a layer', () => {
    it('T18.4.1 should open edit modal to update a category', () => {
      // setup
      let openSpy = spyOn(component, 'openEditModal').and.callThrough();
      let modalSpy = spyOn(component['modalService'], 'open');
      let layer: FirelocLayer = {
        id: 0, designation: '', serverLayer: '', slug: 'slug',
        store: '', style: '', workspace: '', child: null
      };

      component.openEditModal(layer, {});

      expect(openSpy).toHaveBeenCalled();
      expect(component.openLayer).toEqual(layer);
      expect(component.openLayerSlug).toEqual('slug');
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T18.4.2 should update edit layer property when form changes', () => {
      // spies
      let updateSpy = spyOn(component, 'updateEditLayerField').and.callThrough();
      let openLayer: FirelocLayer = {
        id: 0, designation: '', serverLayer: '', slug: '', store: '', style: '', workspace: ''
      }
      component.openLayer = openLayer;
      fixture.detectChanges();

      component.updateEditLayerField('slug1', 'slug');

      // expectations
      expect(updateSpy).toHaveBeenCalledWith('slug1', 'slug');
      expect(component.openLayer.slug).toEqual('slug1');
    });

    it('T18.4.3 should not update a layer if edit layer form is invalid', () => {
      // spies
      let updateSpy = spyOn(component, 'updateLayer').and.callThrough();
      let updateAPISpy = spyOn(component['layerServ'], 'updateLayer');

      component.updateLayer();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).not.toHaveBeenCalled();
    });

    it('T18.4.4 should update a layer (update all fields)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateLayer').and.callThrough();
      let updateAPISpy = spyOn(component['layerServ'], 'updateLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.openLayer = layers[0].child ? layers[0].child[0] : layers[0];

      // fake edit information
      component.editLayerForm.patchValue({
        designation: 'design', slug: 'slug', workspace: 'work', store: 'store', serverLayer: 'server', style: 'style'
      });
      component.editLayerForm.get('designation')?.markAsDirty();
      component.editLayerForm.get('slug')?.markAsDirty();
      component.editLayerForm.get('workspace')?.markAsDirty();
      component.editLayerForm.get('store')?.markAsDirty();
      component.editLayerForm.get('serverLayer')?.markAsDirty();
      component.editLayerForm.get('style')?.markAsDirty();
      fixture.detectChanges();

      component.updateLayer();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).toHaveBeenCalled();
    });

    it('T18.4.5 should update a layer (update one fields)', () => {
      // spies
      let updateSpy = spyOn(component, 'updateLayer').and.callThrough();
      let updateAPISpy = spyOn(component['layerServ'], 'updateLayer').and.returnValue(of({
        id: 1, slug: 'slug', level: 1, rootid: 1, designation: 'design',
        gsrvlyr: 'layer', store: '', style: '', workspace: ''
      }));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.openLayer = layers[0].child ? layers[0].child[0] : layers[0];

      // fake edit information
      component.editLayerForm.patchValue({
        designation: 'design', slug: 'slug', workspace: 'work', store: 'store', serverLayer: 'server', style: 'style'
      });
      component.editLayerForm.get('designation')?.markAsDirty();
      fixture.detectChanges();

      component.updateLayer();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).toHaveBeenCalled();
    });

    it('T18.4.6 should handle error from updating a layer', () => {
      // spies
      let updateSpy = spyOn(component, 'updateLayer').and.callThrough();
      let updateAPISpy = spyOn(component['layerServ'], 'updateLayer').and.returnValue(throwError(() => new Error()));
      let findUpdateSpy = spyOn(component, 'findLayerAndUpdate');

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.openLayer = layers[0].child ? layers[0].child[0] : layers[0];

      // fake edit information
      component.editLayerForm.patchValue({
        designation: 'design', slug: 'slug', workspace: 'work', store: 'store', serverLayer: 'server', style: 'style'
      });
      component.editLayerForm.get('designation')?.markAsDirty();
      fixture.detectChanges();

      component.updateLayer();

      // expectations
      expect(updateSpy).toHaveBeenCalled();
      expect(updateAPISpy).toHaveBeenCalled();
      expect(findUpdateSpy).not.toHaveBeenCalled();
    });
  });

  it('T18.12 should find layer and update it', () => {
    // spies
    let updateSpy = spyOn(component, 'findLayerAndUpdate').and.callThrough();

    let layer: FirelocLayer = {
      id: 1, designation: '', serverLayer: '', slug: '', store: '', style: '', workspace: '', child: [
        { id: 2, child: null, designation: '', serverLayer: '', slug: '', store: '', style: '', workspace: '' }
      ],
    };
    let updatedLayer: FirelocLayer = {
      id: 2, child: null, designation: '', serverLayer: '', slug: '', store: '', style: '', workspace: ''
    };
    component.findLayerAndUpdate(layer, updatedLayer);

    let layer2: FirelocLayer = {
      id: 1, designation: '', serverLayer: '', slug: '', store: '', style: '', workspace: '', child: [
        { id: 2, child: null, designation: '', serverLayer: '', slug: '', store: '', style: '', workspace: '' }
      ],
    };
    let updatedLayer2: FirelocLayer = {
      id: 3, child: null, designation: '', serverLayer: '', slug: '', store: '', style: '', workspace: ''
    };
    component.findLayerAndUpdate(layer2, updatedLayer2);

    let layer3: FirelocLayer = null as unknown as FirelocLayer;
    let updatedLayer3: FirelocLayer = {
      id: 3, child: null, designation: '', serverLayer: '', slug: '', store: '', style: '', workspace: ''
    };
    component.findLayerAndUpdate(layer3, updatedLayer3);

    expect(updateSpy).toHaveBeenCalledTimes(5);
  });

  describe('TS18.5 delete a layer or category', () => {
    it('T18.5.1 should open delete modal to delete a layer/category', () => {
      // setup
      let openSpy = spyOn(component, 'openDeleteModal').and.callThrough();
      let modalSpy = spyOn(component['modalService'], 'open');
      let layer: FirelocLayer = {
        id: 0, designation: '', serverLayer: '', slug: 'slug',
        store: '', style: '', workspace: '', child: null
      };

      component.openDeleteModal(layer, {});

      expect(openSpy).toHaveBeenCalled();
      expect(component.openLayer).toEqual(layer);
      expect(component.isConfChecked).toBeFalse();
      expect(component.hasClickedRemove).toBeFalse();
      expect(modalSpy).toHaveBeenCalled();
    });

    it('T18.5.2 should not delete layer/category without confirmation', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeLayer').and.callThrough();
      let deleteAPISpy = spyOn(component['layerServ'], 'deleteLayer');

      component.removeLayer();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).not.toHaveBeenCalled();
    });

    it('T18.5.3 should delete layer/category if there was confirmation (main category)', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeLayer').and.callThrough();
      let deleteAPISpy = spyOn(component['layerServ'], 'deleteLayer').and.returnValue(of({}));
      let findRemoveSpy = spyOn(component, 'findAndRemoveLayer');

      // fake information
      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.filteredLayers = layers;
      component.isConfChecked = true;
      component.openLayer = layers[0];
      fixture.detectChanges();

      component.removeLayer();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).toHaveBeenCalledWith('slug1');
      expect(component.filteredLayers).toEqual([]);
      expect(component.isConfChecked).toBeFalse();
      expect(component.hasClickedRemove).toBeFalse();
      expect(findRemoveSpy).not.toHaveBeenCalled();
    });

    it('T18.5.4 should delete layer/category if there was confirmation (layer level 3)', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeLayer').and.callThrough();
      let deleteAPISpy = spyOn(component['layerServ'], 'deleteLayer').and.returnValue(of({}));

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.filteredLayers = layers;
      component.isConfChecked = true;
      component.openLayer = layers[0].child && layers[0].child[1].child ? layers[0].child[1].child[0] : layers[0];
      fixture.detectChanges();

      component.removeLayer();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).toHaveBeenCalledWith('slug4');
      expect(component.isConfChecked).toBeFalse();
      expect(component.hasClickedRemove).toBeFalse();
    });

    it('T18.5.5 should handle error from deleting a layer/category', () => {
      // spies
      let deleteSpy = spyOn(component, 'removeLayer').and.callThrough();
      let deleteAPISpy = spyOn(component['layerServ'], 'deleteLayer').and.returnValue(throwError(() => new Error()));
      let findRemoveSpy = spyOn(component, 'findAndRemoveLayer');

      // fake data
      let layers: FirelocLayer[] = [{
        id: 1,
        slug: 'slug1', level: 1, rootID: 1, designation: '', serverLayer: '',
        store: '', style: '', workspace: '', isOpen: true, canOpen: true, child:
          [{
            id: 2,
            slug: 'slug2', level: 2, rootID: 1, designation: 'nope', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
          },
          {
            id: 3,
            slug: 'slug3', level: 2, rootID: 1, designation: '', serverLayer: '',
            store: '', style: '', workspace: '', isOpen: false, canOpen: true, child:
              [{
                id: 4,
                slug: 'slug4', level: 3, rootID: 3, designation: 'name', serverLayer: '',
                store: '', style: '', workspace: '', isOpen: false, canOpen: false, child: null
              }],
          },
          ]
      }];
      component.layers = layers;
      component.filteredLayers = layers;
      component.isConfChecked = true;
      component.openLayer = layers[0].child && layers[0].child[1].child ? layers[0].child[1].child[0] : layers[0];
      fixture.detectChanges();

      component.removeLayer();

      // expectations
      expect(deleteSpy).toHaveBeenCalledWith();
      expect(deleteAPISpy).toHaveBeenCalledWith('slug4');
      expect(component.isConfChecked).toBeFalse();
      expect(component.hasClickedRemove).toBeFalse();
      expect(findRemoveSpy).not.toHaveBeenCalled();
    });
  });

});
