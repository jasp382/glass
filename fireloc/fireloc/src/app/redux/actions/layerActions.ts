import { Injectable } from '@angular/core';
import { NgRedux } from '@angular-redux/store';
import { AppState } from '../reducers';
import { Layer } from 'src/app/interfaces/layers';

/**
 * Redux layer actions. 
 * These actions are meant to be dispatched and caught by {@link layerReducer}.
 */
@Injectable()
export class LayerActions {
    /**
     * Action to store a new layer in redux state
     */
    static ADD_LAYER = 'ADD_LAYER';
    /**
     * Action to remove a stored layer in redux state
     */
    static REMOVE_LAYER = 'REMOVE_LAYER';
    /**
     * Action to clear stored layers in redux state
     */
    static CLEAR_LAYERS = 'CLEAR_LAYERS';

    /**
     * Empty constructor
     * @param ngRedux Redux to dispatch actions
     */
    constructor(private ngRedux: NgRedux<AppState>) { }

    /**
     * Dispatch action to store a new layer in redux state
     * @param layer layer to be added to the state
     */
    addLayer(layer: Layer) {
        this.ngRedux.dispatch({ type: LayerActions.ADD_LAYER, payload: { layer: layer } });
    }

    /**
     * Dispatch action to remove a stored layer in redux state
     * @param layer layer to be removed from the state
     */
    removeLayer(layer: Layer) {
        this.ngRedux.dispatch({ type: LayerActions.REMOVE_LAYER, payload: { layer: layer } });
    }

    /**
     * Dispatch action to clear all layers stored in redux state
     */
    clearLayers() {
        this.ngRedux.dispatch({ type: LayerActions.CLEAR_LAYERS });
    }

}