// Graph interfaces

import { ApiStatus } from "./general"

/**
 * INterface for Graph Series data point
 */
export interface GeoChartDataPoint {
    /**
     * point x value
     */
    x: number,
    /**
     * point y value
     */
    y: number
}

/**
 * Interface for Graph Series
 */
export interface GeoChartSeries {
    /**
     * series ID
     */
    id: number,
    /**
     * series slug
     */
    slug: string,
    /**
     * series name
     */
    name: string,
    /**
     * series color
     */
    color: string
    /**
     * list of points in the series
     */
    points: GeoChartDataPoint[],
}

/**
 * Interface for Graphs
 */
export interface GeoChart {
    /**
     * graph ID
     */
    id: number,
    /**
     * graph slug
     */
    slug: string,
    /**
     * graph title
     */
    designation: string,
    /**
     * graph subtitle
     */
    description: string,
    /**
     * graph type. Acceptable types are BAR, LINE, PIE or SCATTER
     */
    chartType: string,
    /**
     * graph user group ID
     */
    userGroupID?: number,
    /**
     * list of graph series
     */
    series: GeoChartSeries[]
}

export interface ChartSeries {
    id: number,
    slug: string,
    color: string,
    name: string,
    chartid: number
}

export interface Chart {
    id: number,
    slug: string,
    designation: string,
    description: string,
    chartype: string,
    series: ChartSeries[]
}

export interface ChartApi {
    data: Chart[],
    status: ApiStatus
}