import { Action } from 'redux';

/**
 * Interface to Redux action
 */
export interface ActionPayload extends Action {
    /**
     * Redux action payload (can transport anything)
     */
    payload: any;
}