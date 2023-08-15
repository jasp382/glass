import { datetimeToRequestString, numberFormatter, pointsToWKTF } from "./formatter";

describe('TS81 Formatter Functions', () => {

    it('T81.1 should format big number to improve readability', () => {
        // 0
        const result0 = numberFormatter(0);
        expect(result0).toEqual('0');
        // 10
        const result10 = numberFormatter(10);
        expect(result10).toEqual('10');
        // 1.000
        const result1k = numberFormatter(1000);
        expect(result1k).toEqual('1K');
        // 1.000.000
        const result1M = numberFormatter(1000000);
        expect(result1M).toEqual('1M');
    });

    it('T81.2 should format point array to WKT format', () => {
        let points = [
            [40.5, -8.0],
            [40.5, -7.5],
            [40.0, -7.5],
            [40.0, -8.0],
            [40.5, -8.0],
        ];
        let expectedResult = 'POLYGON((-8 40.5,-7.5 40.5,-7.5 40,-8 40,-8 40.5))';
        const result = pointsToWKTF(points);
        expect(result).toEqual(expectedResult);
    });

    it('T81.3 should format datetime string to API request format', () => {
        let datetime = '2022-12-01T21:30';
        const result = datetimeToRequestString(datetime);
        let expectedResult = '2022-12-01 21:30:00';
        expect(result).toEqual(expectedResult);
    });

});