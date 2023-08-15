import { NgRedux } from "@angular-redux/store";
import { MockNgRedux } from "@angular-redux/store/testing";
import { Layer } from "src/app/interfaces/layers";
import { LayerActions } from "./layerActions";

describe('TS50 Redux LayerActions', () => {
    let mockNgRedux: NgRedux<any>;
    let layerActions: LayerActions;

    beforeEach(() => {
        MockNgRedux.reset();
        mockNgRedux = MockNgRedux.getInstance();
        layerActions = new LayerActions(mockNgRedux);
    });

    it('T50.1 should dispatch add layer', () => {
        // fake data
        let layer: Layer = {
            id: 1,
            level: 1,
            title: "t",
            serverLayer: null,
            slug: null,
            store: null,
            style: null,
            workspace: null,
            child: null,
            isOpen: false
        }
        // expected action and spy
        const expectedAction = {
            type: LayerActions.ADD_LAYER,
            payload: {
                layer: layer
            }
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        layerActions.addLayer(layer);

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T50.2 should dispatch remove layer', () => {
        // fake data
        let layer: Layer = {
            id: 1,
            level: 1,
            title: "t",
            serverLayer: null,
            slug: null,
            store: null,
            style: null,
            workspace: null,
            child: null,
            isOpen: false
        }
        // expected action and spy
        const expectedAction = {
            type: LayerActions.REMOVE_LAYER,
            payload: {
                layer: layer
            }
        };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        layerActions.removeLayer(layer);

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });

    it('T50.3 should dispatch clear layers', () => {
        // expected action and spy
        const expectedAction = { type: LayerActions.CLEAR_LAYERS };
        const dispatchSpy = spyOn(mockNgRedux, 'dispatch');

        // call action
        layerActions.clearLayers();

        // expectations
        expect(dispatchSpy).toHaveBeenCalledOnceWith(expectedAction);
    });
});