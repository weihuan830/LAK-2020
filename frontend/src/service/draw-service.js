import * as d3 from 'd3'
import DataService from './data-service'
var userKey1 = {
    "4883": 1,
    "10201": 1,
    "18648": 1,
    "14153": 1,
    "22352": 1,
    "13372": 1,
    "21414": 1,
    "18470": 1,
}
var userKey2 = {
    "19924": 1,
    "22818": 1,
    "5467": 1,
    "5785": 1,
    "9514": 1,
    "21594": 1,
    "10940": 1,
}
var gcount = 0;
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
                let thisDate = dates[index],
                    dateParts = thisDate.split(/\//),
                    fullDate = new Date(dateParts[2], dateParts[0] - 1, dateParts[1]);
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
            let minAndMax = getMinAndMax(dates),
                dayOfWeek = {}
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
        if (data[0] && typeof(data[0]) != "string" && data[0][1]) {
            values = data.map((item, i) => parseInt(item[1]))
        } else {
            values = data.map((item, i) => parseInt(item))
        }

        function average(data) {
            let sum = data.reduce(function(sum, value) {
                return sum + value;
            }, 0);
            let avg = sum / data.length;
            return avg;
        }
        let avg = average(values);

        let squareDiffs = values.map(function(value) {
            let diff = value - avg;
            let sqrDiff = diff * diff;
            return sqrDiff;
        });

        let avgSquareDiff = average(squareDiffs);

        let stdDev = Math.sqrt(avgSquareDiff);
        return stdDev;
    }
    drawParaChart(data, config) {
        let localdata = []
        let tmp = [this.getWeekDay(data[0][2])]
        for (let i = 0; i < data.length - 1; i++) {
            if (DrawService.ifSameWeek(data[i][2], data[i + 1][2])) {
                // tmp.push(data[i+1])
                tmp.push(this.getWeekDay(data[i + 1][2]))

            } else {
                localdata.push(tmp)
                tmp = []
                tmp.push(this.getWeekDay(data[i + 1][2]))
            }
        }
        console.log(localdata)
        return localdata
    }
    drawStdScore(data, config) {
        let stdstd = []
        let std = []
        let span = 5
        let avg = []
        let stdavg = []
        let userid = []
        let color = []
        let diffscore = []
        let getcolorRange = d3.scaleLinear().domain([-50, 50])
            .range(['red', 'green'])
            .interpolate(d3.interpolateHcl)
        for (let key in data) {
            let tmpstd = []
            let dtki = data[key]
            let _ti = dtki.reduce((a, b) => (a + parseInt(b[1])), 0) / dtki.length
            avg.push(_ti)
            for (let t = 0; t < dtki.length; t++) {
                if ((t + 1) * span >= dtki.length) {
                    tmpstd.push(DrawService._standardDev(dtki.slice(t * span, dtki.length)))
                    break;
                } else {
                    tmpstd.push(DrawService._standardDev(dtki.slice(t * span, (t + 1) * span)))
                }
            }
            let _tmpi = DrawService._standardDev(tmpstd)
                // std.push(_tmp)
            std.push(_tmpi)
            userid.push(key)
        }
        console.log(userid)
            // ["8259", "8288", "8486"]  <=20
            // ["4533", "4643", "4951", "5152", "10891"] (20, 30]
            // ["5569"] (30, 40]
            // ["5446", "5577"] (40, 50]
            // ["4270"] 50-60

        // for (let i = 0; i < std.length; i++) {
        //     stdstd.push(DrawService._standardDev(std[i]))
        //     stdavg.push(std[i].reduce((a, b) => (a + b), 0) / std[i].length)
        // }
        // console.log(stdstd)
        let width = 800;
        let height = 500;
        let margin_left = 50;
        let margin_bottom = 50;
        let currenData = std
        let currentMax = Math.max(...currenData)
        let xScale = d3.scaleLinear().domain([0, currentMax]).range([0 + margin_left, width + margin_left]);
        let yScale = d3.scaleLinear().domain([0, Math.max(...avg)]).range([height, 0]);
        let coun = [0, 0, 0, 0]
        let cateusers = [{}, {}, {}, {}, {}, {}]

        function getcolor(score, i) {
            if (Math.abs(diffscore[i]) >= 10)
                return getcolorRange(diffscore[i])
            else
                return "black"
                    // if (userKey2[userid[i]]) {
                    //     gcount++;
                    //     console.log(gcount)
                    //     return "black"
                    // }
                    // if (score >= 90) {
                    //     cateusers[0][userid[i]] = score
                    //     coun[0]++
                    //         return "#00FF00"
                    // } else if (score >= 70) {
                    //     cateusers[1][userid[i]] = score
                    //     coun[1]++
                    //         return "#6AFF00"
                    // } else if (score >= 50) {
                    //     cateusers[2][userid[i]] = score
                    //     coun[2]++
                    //         return "#C2FF00"
                    // } else if (score >= 30) {
                    //     cateusers[3][userid[i]] = score
                    //     coun[3]++
                    //         return "#FFE400"
                    // } else if (score > 10) {
                    //     cateusers[4][userid[i]] = score
                    //     coun[4]++
                    //         return "#FF6900"
                    // } else {
                    //     coun[5]++
                    //         cateusers[5][userid[i]] = score
                    //     return "#FF0000"
                    // }
        }
        let svg = d3.select("#" + config.svgid).attr("width", width + margin_left).attr("height", height + margin_bottom)
        svg.selectAll(".dot")
            .data(currenData)
            .enter().append("circle")
            .attr("class", "dot") // Assign a class for styling
            .attr("cx", function(d, i) { return xScale(d) })
            .attr("cy", function(d, i) { return yScale(avg[i]) + 10 })
            .attr("r", 2)
            .attr("opacity", function(d, i) {
                if (Math.abs(diffscore[i]) < 10)
                    return 0
            })
            .attr("fill", (d, i) => getcolor(avg[i], i))
        let xAxis = d3.axisBottom(xScale).ticks(5);
        let yAxis = d3.axisLeft(yScale).ticks(10);
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${(height+10)})`)
            .call(xAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "translate(" + (width - 30) + ",10)")
            .attr("fill", "#000")
            .text("User Score Standard deviation");
        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + margin_left + ",10)")
            .call(yAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "translate(-50,10) rotate(-90)")
            .attr("fill", "#000")
            .text("AVG score");
        DataService.Users = cateusers
    }
    drawDifficulty(data, config) {
        let std = []
        let quat = []
        let diff = []
        for (let key in data) {
            quat.push(data[key]["seq"].length)
            std.push(DrawService._standardDev(data[key]["seq"]))
            diff.push(parseInt(data[key]["level"]))
        }
        let width = 500;
        let height = 500;
        let margin_left = 50;
        let margin_bottom = 50;
        let xScale = d3.scaleLinear().domain([0, Math.max(...diff)]).range([0 + margin_left, width + margin_left]);
        let yScale = d3.scaleLinear().domain([0, Math.max(...std)]).range([height, 0]);
        let rScale = d3.scaleLinear().domain([Math.min(...quat), Math.max(...quat)]).range([1, 10]);
        let svg = d3.select("#" + config.svgid).attr("width", width + margin_left + 10).attr("height", height + margin_bottom + 10)
        let xAxis = d3.axisBottom(xScale).ticks(5);
        let yAxis = d3.axisLeft(yScale).ticks(10);
        let getcolor = d3.scaleLinear().domain([Math.min(...quat), Math.max(...quat)])
            .range(['green', 'red'])
            .interpolate(d3.interpolateHcl)
        svg.selectAll(".dot")
            .data(diff)
            .enter().append("circle")
            .attr("class", "dot") // Assign a class for styling
            .attr("cx", function(d, i) { return xScale(d) })
            .attr("cy", function(d, i) { return yScale(std[i]) + 10 })
            .attr("r", (d, i) => rScale(quat[i]))
            .attr("fill", function(d, i) { return getcolor(quat[i]) })
            .attr("opacity", 0.3)
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${(height+10)})`)
            .call(xAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "translate(" + width + ",10)")
            .attr("fill", "#000")
            .text("Labeled difficulty level");
        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + margin_left + ",10)")
            .call(yAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "translate(-50,10) rotate(-90)")
            .attr("fill", "#000")
            .text("Problem Score Standard deviation");
    }
    drawLineChart(data, config) {
        let usercat = DataService.Users
        let width = config.width;
        let height = config.height;
        let margin_left = 50;
        let margin_bottom = 50;
        let svg = d3.select("#" + config.svgid).attr("width", width + margin_left).attr("height", height + margin_bottom)
            // let span = config.span;
        let span = 10
        let alldata = []
        let userlist = []
        for (let i = 0; i < data.length; i++) {
            let tmp = data[i][2]
            let tmp2 = []
            userlist.push(data[i][0])
            for (let t = 0; t < tmp.length; t++) {
                tmp2.push([t, parseInt(tmp[t][1]), tmp[t][2]])
            }
            let stepavgs = []
            for (let t = 0; t < tmp2.length; t++) {
                // time, score, weekday
                // if ((t + 1) * span >= tmp2.length) {
                //     stepavgs.push([t, tmp2.slice(t * span, tmp2.length).reduce((a, b) => (a + b[1]), 0) / (tmp2.length - t * span), this.getWeekDay(tmp2[t * span][2])])
                //     break
                // } else {
                //     stepavgs.push([t, tmp2.slice(t * span, (t + 1) * span).reduce((a, b) => (a + b[1]), 0) / span, this.getWeekDay(tmp2[t * span][2])])
                // }
                // std deviation
                if ((t + 2) * span >= tmp2.length) {
                    stepavgs.push([t, DrawService._standardDev(tmp2.slice(t * span, tmp2.length))])
                    break
                } else {
                    stepavgs.push([t, DrawService._standardDev(tmp2.slice(t * span, (t + 2) * span))])
                }

            }
            alldata.push(stepavgs)
        }
        let maxlen = alldata[0].length
            /* Scale */
        let xScale = d3.scaleLinear().domain([0, maxlen]).range([0 + margin_left, width + margin_left]);
        let yScale = d3.scaleLinear().domain([0, 50]).range([height, 0]);
        let color = d3.scaleOrdinal(d3.schemeCategory10);
        let selectedUser = {}
        let scorecolor = d3.scaleLinear().domain([50, 80])
            .range(['red', 'green'])
            .interpolate(d3.interpolateHcl)

        function getcolor(user, i) {
            if (usercat[0][user]) {
                return "none"
                return 'green'
            } else if (usercat[1][user]) {
                selectedUser[user] = alldata[i]
                return scorecolor(DataService.Users[1][user])
                return 'blue'
            } else if (usercat[2][user]) {
                return "none"
                return 'red'
            }
            return "none"
            return "black"
        }
        /* Add line into SVG */
        let line = d3.line().curve(d3.curveBasis).x(d => xScale(d[0])).y(d => yScale(d[1]));
        let lines = svg.append('g').attr('class', 'lines');
        lines.selectAll('.line-group')
            .data(alldata).enter()
            .append('g')
            .attr('class', 'line-group')
            .append('path')
            .attr('class', 'line')
            .attr('d', d => line(d))
            .attr("fill", "none")
            .style('stroke', (d, i) => getcolor(userlist[i], i))
        let xAxis = d3.axisBottom(xScale).ticks(20);
        let yAxis = d3.axisLeft(yScale).ticks(10);
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${height})`)
            .call(xAxis);
        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + margin_left + ",0)")
            .call(yAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "translate(-50,10) rotate(-90)")
            .attr("fill", "#000")
            .text("Total values");
        DataService.selectedUser = selectedUser
    }
    drawStepStd(data, config) {
        let userids = [
                ["5152"][0]
            ] // <50

        // ["8259", "8288", "8486"]  <=20
        // ["4533",  "4951", "4643", "5152", "10891"] (20, 30]
        // ["5569"] (30, 40]
        // ["5446", "5577"] (40, 50]
        // ["4270"] 50-60

        let stepNum = 5

        function data2steps(uid, arr) {
            let avgstd = []
            for (let i = 0; i < arr.length; i += stepNum) {
                // console.log(i)
                let d = []
                if (i + stepNum * 2 < arr.length) {
                    d = arr.slice(i, i + stepNum * 2);
                } else {
                    d = arr.slice(i, arr.length);
                }
                avgstd.push([d.reduce((a, b) => (a + parseInt(b[1])), 0) / d.length, DrawService._standardDev(d.slice(0, d.length))])
            }
            return avgstd
        }
        let processed = [];
        for (let key in data) {
            let tmp = data2steps(key, data[key]);
            // if(tmp[0][0] >=80 ){
            if (userids.includes(key))
                processed.push(tmp)
                // }
                // break
        }
        let width = 1200;
        let height = 500;
        let margin_left = 50;
        let margin_bottom = 50;
        let xScale = d3.scaleLinear().domain([0, 30]).range([0 + margin_left, width + margin_left]);
        let yScale = d3.scaleLinear().domain([0, 50]).range([height, 0]); // std
        let getcolor = d3.scaleLinear().domain([0, 100])
            .range(['red', 'green'])
            .interpolate(d3.interpolateHcl)
        let svg = d3.select("#" + config.svgid).attr("width", width + margin_left).attr("height", height + margin_bottom)
        var valueline = d3.line()
            .x(function(d, i) { return xScale(i); })
            .y(function(d, i) { return yScale(d[1]); })
            // d3.line().curve(d3.curveBasis).x(d => xScale(d[0])).y(d => yScale(d[1]));
        let lines = svg.append('g').attr('class', 'lines');
        lines.selectAll('.line-group')
            .data(processed).enter()
            .append('g')
            .attr('class', 'line-group')
            .append('path')
            .attr('class', 'line')
            .attr("stroke", function(d, i) {
                return "green"
                    // return getcolor((d[0][d[0].length-1] + d[0][d[0].length-2])/2)
            })
            .attr("fill", "none")
            .attr("stroke-width", 1)
            .attr("d", d => valueline(d));

        let xAxis = d3.axisBottom(xScale).ticks(5);
        let yAxis = d3.axisLeft(yScale).ticks(10);
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${(height+10)})`)
            .call(xAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "translate(" + (width - 30) + ",10)")
            .attr("fill", "#000")
            .text("Step");
        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + margin_left + ",10)")
            .call(yAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "translate(-50,10) rotate(-90)")
            .attr("fill", "#000")
            .text("Std");
    }
    drawSelectedUsers(data, config) {
        let std = []
        let avg = []
        let userid = []
        for (let key in data) {
            avg.push(data[key].reduce((a, b) => (a + parseInt(b[1])), 0) / data[key].length)
            userid.push(key)
            std.push(DrawService._standardDev(data[key].slice(0, data[key].length)))
        }
        let width = 800;
        let height = 500;
        let margin_left = 50;
        let margin_bottom = 50;
        let xScale = d3.scaleLinear().domain([0, Math.max(...std)]).range([0 + margin_left, width + margin_left]);
        let yScale = d3.scaleLinear().domain([0, Math.max(...avg)]).range([height, 0]);
        let getcolor = d3.scaleLinear().domain([50, 80])
            .range(['red', 'green'])
            .interpolate(d3.interpolateHcl)
        let svg = d3.select("#" + config.svgid).attr("width", width + margin_left).attr("height", height + margin_bottom)
        svg.selectAll(".dot")
            .data(std)
            .enter().append("circle")
            .attr("class", "dot") // Assign a class for styling
            .attr("cx", function(d, i) { return xScale(d) })
            .attr("cy", function(d, i) { return yScale(avg[i]) })
            .attr("r", 2)
            .attr("fill", (d, i) => {
                // console.log(userid[i], DataService.Users)
                return getcolor(parseInt(DataService.Users[1][userid[i]]))
            })
            // .attr("fill", "black")
        let xAxis = d3.axisBottom(xScale).ticks(5);
        let yAxis = d3.axisLeft(yScale).ticks(10);
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${(height+10)})`)
            .call(xAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "translate(" + (width - 30) + ",10)")
            .attr("fill", "#000")
            .text("Std--std");
        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + margin_left + ",10)")
            .call(yAxis)
            .append('text')
            .attr("y", 15)
            .attr("transform", "translate(-50,10) rotate(-90)")
            .attr("fill", "#000")
            .text("AVG std");
    }
    drawHistgram(svg, data, config) {
        let color = d3.scaleOrdinal(d3.schemeCategory10);
        let height = 1000
        let width = 300
        let localdata = {}
        data.forEach(d => {
            d.forEach(t => {
                if (localdata[t[2]]) {
                    localdata[t[2]].push(t[1])
                } else {
                    localdata[t[2]] = [t[1]]
                }
            })
        })
        let count = 0
        for (let key in localdata) {
            console.log(key)
            let tmpdata = localdata[key]
            let grade = {}
            tmpdata.forEach(item => {
                if (grade[item]) {
                    grade[item] += 1
                } else {
                    grade[item] = 1
                }
            })
            let scaleX = d3.scaleBand().domain(Object.keys(grade)).range([0, width])
            let scaleY = d3.scaleLinear().domain([0, 500]).range([0, height]);
            let localg = svg.append("g").attr("transform", "translate(" + (count * width + count * 50) + ",0)").call(d3.axisBottom(scaleX));
            count++;
            let dataarr = []
            for (let key in grade) {
                dataarr.push([key, grade[key]])
            }
            localg.selectAll('rect.bar')
                .data(dataarr)
                .enter().append('rect')
                .attr("class", "bar")
                .attr("width", scaleX.bandwidth())
                .attr("fill", (d, i) => color(i))
                .attr("height", function(d) { return scaleY(d[1]); })
                .attr("x", function(d) { return scaleX(d[0]); })
                .attr("y", function(d) { return -scaleY(d[1]); })
                .attr("transform", "translate(0," + height + ")")
        }

    }

}
const DrawService = new Service()
export default DrawService