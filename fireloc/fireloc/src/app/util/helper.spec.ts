import { Geom } from "../interfaces/contribs";
import { avgLatLong, checkUserHasPermissions, getDateTimeValues, getLatLongValues } from "./helper";

describe('TS82 Helper Functions', () => {
    it('T82.1 should check if user has special permissions', () => {
        let storageSpy = spyOn(Storage.prototype, 'getItem');
        // justauser
        storageSpy.and.returnValue('justauser');
        const resultUser = checkUserHasPermissions(true);
        expect(resultUser).toBeFalse();
        // volunteer
        storageSpy.and.returnValue('volunteer');
        const resultVolunteer = checkUserHasPermissions(true);
        expect(resultVolunteer).toBeFalse();
        // fireloc
        storageSpy.and.returnValue('fireloc');
        const resultFireloc = checkUserHasPermissions(true);
        expect(resultFireloc).toBeTrue();
        // superuser
        storageSpy.and.returnValue('superuser');
        const resultSuper = checkUserHasPermissions(true);
        expect(resultSuper).toBeTrue();
        // not logged
        const result = checkUserHasPermissions(false);
        expect(result).toBeFalse();
    });

    it('T82.2 should get average latitude and longitude from values', () => {
        let values: Geom[] = [{ pid: 1, lat: 10, long: 10 }, { pid: 2, lat: 2, long: 2 }];
        let result = avgLatLong(values);
        expect(result[0]).toBe('6.000');
        expect(result[1]).toBe('6.000');
    });

    it('T82.3 should get values for latitude and longitude from point string', () => {
        let point = '(-8.408286 40.195120)';
        let result = getLatLongValues(point);
        expect(result[0]).toBe(-8.408286);
        expect(result[1]).toBe(40.195120);
    });

    it('T82.4 should get datetime values from datehour string', () => {
        let date = '2022-03-23 19:26:33';
        let resultStringPT = getDateTimeValues(date, true, 'pt');
        expect(resultStringPT[0]).toBe(2022);
        expect(resultStringPT[1]).toBe('Março');
        expect(resultStringPT[2]).toBe(23);
        expect(resultStringPT[3]).toBe('19');
        expect(resultStringPT[4]).toBe('26');

        let resultStringEN = getDateTimeValues(date, true, 'en');
        expect(resultStringEN[0]).toBe(2022);
        expect(resultStringEN[1]).toBe('March');
        expect(resultStringEN[2]).toBe(23);
        expect(resultStringEN[3]).toBe('19');
        expect(resultStringEN[4]).toBe('26');
        
        let resultNumber = getDateTimeValues(date, false, 'pt');
        expect(resultNumber[0]).toBe(2022);
        expect(resultNumber[1]).toBe(3);
        expect(resultNumber[2]).toBe(23);
        expect(resultNumber[3]).toBe('19');
        expect(resultNumber[4]).toBe('26');
    });
});