export interface Layers {
  id: number,
  alias: string,
  design: string,
  islayer: boolean,
  style: string,
  classes: string[]|null
}


export interface Geometry {
  id: number,
  code: string,
  name: string,
  geom: string,
  layerid: number
}

export interface GeoServerLayerJson {
  message: string
}

export interface GeoserverLayerResponse {
  status: number,
  json: GeoServerLayerJson,
  http: number
}

export interface StyleData {
  classes : string[],
  red : number[],
  blue: number[],
  green: number[]
}

export interface LayersVis {
  wmsname: string,
  name: string,
  layer: any,
  active: boolean
}