import { ActionReducerMap } from "@ngrx/store";

// Reducers and Stores
import { langReducer, LangState } from "./lang/lang.reducer";
import { loginReducer, LoginState } from "./login/login.reducer";
import { fireEventsReducer, FireEventsState } from './events/events.reducer';
import { contribReducer, ContribState } from "./ctb/ctb.reducer";
import { firelocReducer, FirelocState } from "./flocs/flocs.reducer";
import { chartsReducer, ChartState } from "./charts/charts.reducer";
import { treeLayerReducer, TreeLayerState } from "./geolyr/geolyr.reducer";
import { leafMapReducer, LeafmapState } from "./leaf/leaf.reducer";
import { userReducer, UsersState } from "./users/users.reducer";
import { clusterLayerReducer, ClusterLayerState } from "./clusterlyr/clyr.reducer";

// Effects
import { LangEffects } from "./lang/lang.effects";
import { LoginEffects } from "./login/login.effects";
import { FireEventsEffects } from "./events/events.effects";
import { ContribEffects } from "./ctb/ctb.effects";
import { FirelocEffects } from "./flocs/flocs.effects";
import { ChartsEffects } from "./charts/charts.effects";
import { TreeLayerEffects } from "./geolyr/geolyr.effects";
import { LeafmapEffects } from "./leaf/leaf.effects";
import { UserEffects } from "./users/users.effects";
import { ClusterLayerEffects } from "./clusterlyr/clyr.effects";


export interface AppState {
    lang         : LangState,
    login        : LoginState,
    fireevents   : FireEventsState,
    contrib      : ContribState,
    fireloc      : FirelocState,
    charts       : ChartState,
    treelayer    : TreeLayerState,
    leafmap      : LeafmapState,
    users        : UsersState,
    clusterlayer : ClusterLayerState
}

export const appReducer: ActionReducerMap<AppState> = {
    lang         : langReducer,
    login        : loginReducer,
    fireevents   : fireEventsReducer,
    contrib      : contribReducer,
    fireloc      : firelocReducer,
    charts       : chartsReducer,
    treelayer    : treeLayerReducer,
    leafmap      : leafMapReducer,
    users        : userReducer,
    clusterlayer : clusterLayerReducer,
}

export const appEffects = [
    LangEffects,
    LoginEffects,
    FireEventsEffects,
    ContribEffects,
    FirelocEffects,
    ChartsEffects,
    TreeLayerEffects,
    LeafmapEffects,
    UserEffects,
    ClusterLayerEffects
]