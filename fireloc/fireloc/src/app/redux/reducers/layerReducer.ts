import { tassign } from "tassign";
import { LayerActions } from "../actions/layerActions";
import { Layer } from "src/app/interfaces/layers";

/**
 * Interface used for Layer state in Redux. 
 * Used for geoportal map.
 */
interface LayerState {
	/**
	 * list of geospatial layers stored
	 */
	layers: Layer[]
}

/**
 * Initial Layer state in Redux.
 * Initializes state with empty list.
 */
const INITIAL_STATE_LAYER: LayerState = { layers: [] };

/**
 * Redux layer reducer.
 * Checks dispatched action and updates the layer state with provided payload.
 * 
 * See {@link LayerActions} for possible actions.
 * @param state Redux Layer State. If none provided, initial state is used.
 * @param action dispatched action from redux
 * @returns new layer state
 */
function layerReducer(state: LayerState = INITIAL_STATE_LAYER, action: any) {
	switch (action.type) {
		// add layer
		case LayerActions.ADD_LAYER: return tassign(state, { layers: [...state.layers, action.payload.layer] });
		// remove layer
		case LayerActions.REMOVE_LAYER: return tassign(state, { layers: state.layers.filter(layer => layer !== action.payload.layer) });
		// clear all layers
		case LayerActions.CLEAR_LAYERS: return tassign(state, { layers: <Layer[]>[], });
		default: return state;
	}
}

export { LayerState, layerReducer, INITIAL_STATE_LAYER };