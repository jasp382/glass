import { Layer } from "src/app/interfaces/layers";
import { LayerActions } from "../actions/layerActions";
import { INITIAL_STATE_LAYER, layerReducer, LayerState } from "./layerReducer";

describe('TS59 Redux LayerReducer', () => {
    let initialState: LayerState;

    beforeEach(() => {
        initialState = INITIAL_STATE_LAYER;
    });

    it('T59.1 should add layer', () => {
        // fake data
        let layer: Layer = {
            id: 0,
            level: 0,
            title: "t",
            serverLayer: null,
            slug: null,
            store: null,
            style: null,
            workspace: null,
            child: null,
            isOpen: false
        }
        // expected final state
        let finalState = { layers: [layer] };
        // action to be used
        let action = {
            type: LayerActions.ADD_LAYER,
            payload: {
                layer: layer
            }
        };

        // call reducer
        let state = layerReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T59.2 should remove layer', () => {
        // fake data
        let layer: Layer = {
            id: 0,
            level: 0,
            title: "t",
            serverLayer: null,
            slug: null,
            store: null,
            style: null,
            workspace: null,
            child: null,
            isOpen: false
        }
        initialState = { layers: [layer] };

        // expected final state
        let finalState = { layers: [] };
        // action to be used
        let action = {
            type: LayerActions.REMOVE_LAYER,
            payload: {
                layer: layer
            }
        };

        // call reducer
        let state = layerReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T59.3 should clear layers', () => {
        // expected final state
        let finalState = { layers: [] };
        // action to be used
        let action = { type: LayerActions.CLEAR_LAYERS, };

        // call reducer
        let state = layerReducer(initialState, action);
        // expectation
        expect(state).toEqual(finalState);
    });

    it('T59.4 should not change state when an unexpected action is dispatched', () => {
        // expected final state
        let finalState = INITIAL_STATE_LAYER;
        // action to be used
        let action = { type: '' };

        // call reducer
        let state = layerReducer(undefined, action);
        // expectation
        expect(state).toEqual(finalState);
    });
});