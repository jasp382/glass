import { enMonths, ptMonths } from "../constants/dateMonths";
import { Geom } from "../interfaces/contribs";

/**
 * Helper function that checks whether a user has special permission privileges
 * or not according to their user role.
 * @param {boolean} isLoggedIn value for user login status.
 * @returns {boolean} value for permissions privileges
 * @function
 * 
 * ```typescript
 * let hasPermissions: boolean;
 * hasPermissions = checkUserHasPermissions(true);
 * ```
 */
export const checkUserHasPermissions = (isLoggedIn: boolean): boolean => {
    if (isLoggedIn) {
        // if user is not justauser or volunteer
        let userRole = localStorage.getItem('user_role');
        if (userRole !== 'justauser' && userRole !== 'volunteer') {
            return true;
        }
    }
    return false;
}

/**
 * Helper function that calculates average latitude and longitude from a given point list.
 * @param values array of points with latitude and longitude
 * @returns 2 item array with latitude and longitude as strings with 3 decimal points
 * @function
 * 
 * ```typescript
 * let averages: string[];
 * let points: Geom[] = [{lat:1, long:1, pid: 1}, {lat:2, long: 2, pid: 2}];
 * averages = avgLatLong(points);
 * ```
 */
export const avgLatLong = (values: Geom[]): string[] => {
    // average latitude
    let averageLat = values.reduce((a, b) => {
        return { lat: a.lat + b.lat, long: 0, pid: 0 }
    }).lat / values.length;
    // average longitude
    let averageLong = values.reduce((a, b) => {
        return { long: a.long + b.long, lat: 0, pid: 0 }
    }).long / values.length;

    // return values in string to 3 decimal points
    return [averageLat.toFixed(3), averageLong.toFixed(3)];
}

/**
 * Helper function that deconstructs point string into latitude and longitude values
 * @param point string containing coordinates information in (a b) format
 * @returns array with latitude and longitude values
 * @function
 * 
 * ```typescript
 * let coordinates: number[];
 * let point: string = "(1.2 -2.1)";
 * coordinates = getLatLongValues(point);
 * ```
 */
export const getLatLongValues = (point: string): number[] => {
    let temp1 = point.split('(');
    let temp2 = temp1[1].split(' ');
    let temp3 = temp2[1].split(')');

    // get string values
    let latString = temp2[0];
    let longString = temp3[0];

    // get float values
    let lat = parseFloat(latString);
    let long = parseFloat(longString);

    // return values
    return [lat, long];
}

// deconstruct datetime string into values

/**
 * Helper function that deconstructs datetime string into date values.
 * @param {string} datehour datetime string to convert
 * @param {boolean} monthString value to determine if month wanted in string or number format
 * @param {string} [language] current app language to get appropriate month string
 * @returns array with year, month, day, hours and minutes
 * @function
 * 
 * ```typescript
 * let datetime: string = '2022-12-20T17:38:12Z';
 * let dateValues: number[];
 * let dateValues = getDateTimeValues(datetime, false);
 * ```
 */
export const getDateTimeValues = (datehour: string, monthString: boolean, language?: string): (number | string)[] => {
    // add iOS support for date format (needs [date]T[time]Z format - dates are UTC from API)
    var newDatehour = '';
    if (datehour.includes('T')) newDatehour = datehour;
    else newDatehour = datehour.replace(" ", "T") + "Z";

    let date = new Date(newDatehour);

    // get values
    let year = date.getFullYear();

    let month;
    if (monthString && language === 'pt') month = ptMonths[date.getMonth()].month;
    else if (monthString && language === 'en') month = enMonths[date.getMonth()].month;
    else month = date.getMonth() + 1;

    let day = date.getDate();
    let hourNumber = date.getHours();
    let hour = ('0' + hourNumber).slice(-2);
    let minuteNumber = date.getMinutes();
    let minute = ('0' + minuteNumber).slice(-2);

    // return values
    return [year, month, day, hour, minute];
}