class Service {
    // eslint-disable-next-line no-useless-constructor
    constructor() {

    }
    getWeekDay(dtstr) {
        let gsDayNames = [
            'Sunday',
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday'
        ];
        if (!gsDayNames[(new Date(dtstr)).getDay()]) {
            // console.log(dtstr)
        }
        return gsDayNames[(new Date(dtstr)).getDay()]
    }
    getWeekDayNum(dtstr) {
        return (new Date(dtstr)).getDay()
    }
    ifSameWeek(dtstr1, dtstr2) {
        function getMinAndMax(dates) {
            let result = {};
            for (let index in dates) {
                let thisDate = dates[index]
                    , dateParts = thisDate.split(/\//)
                    , fullDate = new Date(dateParts[2], dateParts[0] - 1, dateParts[1]);
                if (!result['max'] || fullDate > result['max']) {
                    result['max'] = fullDate;
                }
                if (!result['min'] || fullDate < result['min']) {
                    result['min'] = fullDate
                }
            }
            return result;
        }
        function isSameWeek(dates) {
            let minAndMax = getMinAndMax(dates)
                , dayOfWeek = {}
            dayOfWeek['min'] = minAndMax['min'].getDay();
            dayOfWeek['max'] = minAndMax['max'].getDay();
            if (minAndMax['max'] - minAndMax['min'] > 518400000 || dayOfWeek['min'] > dayOfWeek['max']) {
                return false;
            }
            return true;
        }
        return isSameWeek([dtstr1, dtstr2])
    }
    _standardDev(data) {
        let values = []
        if(data[0] && typeof(data[0])!="string" && data[0][1]){
            values = data.map((item,i) => parseInt(item[1]))
        }else{
            values = data.map((item,i) => parseInt(item))
        }
        function average(data) {
            let sum = data.reduce(function (sum, value) {
                return sum + value;
            }, 0);
            let avg = sum / data.length;
            return avg;
        }
        let avg = average(values);
        let squareDiffs = values.map(function (value) {
            let diff = value - avg;
            let sqrDiff = diff * diff;
            return sqrDiff;
        });
        let avgSquareDiff = average(squareDiffs);
        let stdDev = Math.sqrt(avgSquareDiff);
        return stdDev;
    }
    _average(data) {
        let values = []
        if(data[0] && typeof(data[0])!="string" && data[0][1]){
            values = data.map((item,i) => parseInt(item[1]))
        }else{
            values = data.map((item,i) => parseInt(item))
        }
        let sum = values.reduce(function (sum, value) {
            return sum + value;
        }, 0);
        let avg = sum / values.length;
        return avg;
    }
}
const CommonTool = new Service()
export default CommonTool