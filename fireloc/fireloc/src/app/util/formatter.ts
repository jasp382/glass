/**
 * Format numbers for better readability. 1 thousand is 1K, 1 million is 1M and so forth. 
 * Numbers under 1 thousand are returned with the same format.
 * @param {number} num number to format
 * @returns {string} string with formatted number
 * @function
 * 
 * ```typescript
 * let number: number = 1000000;
 * let formattedNumber:string = numberFormatter(number); // 1M
 * ```
 */
export const numberFormatter = (num: number): string => {
    const lookup = [
        { value: 1, symbol: "" },
        { value: 1e3, symbol: "K" },
        { value: 1e6, symbol: "M" },
        { value: 1e9, symbol: "G" },
        { value: 1e12, symbol: "T" },
        { value: 1e15, symbol: "P" },
        { value: 1e18, symbol: "E" }
    ];
    const rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
    var item = lookup.slice().reverse().find(function (item) {
        return num >= item.value;
    });
    return item ? (num / item.value).toFixed(0).replace(rx, "$1") + item.symbol : "0";
}

/**
 * Format points array with latitude and longitude to Well Know Text Format.
 * This usage is limited to POLYGON since it is the only necessary geometry.
 * @param points array of points to format
 * @returns {string} string in WKT format of given points
 * 
 * ```typescript
 * let points: number[] = [[1,2], [1,3]];
 * let wktf:string = pointsToWKTF(points); // POLYGON((2 1, 3 1))
 * ```
 */
export const pointsToWKTF = (points: any[]): string => {
    let wktf = 'POLYGON((';

    for (let index = 0; index < points.length; index++) {
        // add ',' to point set except last set
        if (index != points.length - 1) wktf += `${points[index][1]} ${points[index][0]},`;
        else wktf += `${points[index][1]} ${points[index][0]}`;
    }

    wktf += '))';
    return wktf;
}

// event date request format
/**
 * Format datetime string into string format required by API.
 * @param {string} datetime string with date values to format
 * @returns date in YYYY-MM-DD hh:mm:ss format
 * 
 * ```typescript
 * let datetime: string = '2022-12-20T17:38:12Z';
 * let wtf:string = datetimeToRequestString(datetime); // 2022-12-20 17:38:12
 * ```
 */
export const datetimeToRequestString = (datetime: string): string => {
    let date = new Date(datetime);
    let day = ("0" + date.getDate()).slice(-2);
    let month = ("0" + (date.getMonth() + 1)).slice(-2);
    let year = date.getFullYear();
    let hours = ("0" + date.getHours()).slice(-2);
    let minutes = ("0" + date.getMinutes()).slice(-2);
    let seconds = '00';

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}