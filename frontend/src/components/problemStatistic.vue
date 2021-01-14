<template>
  <div>
    <svg :id="svgid"></svg>
    <svg :id="svgnormal"></svg>
  </div>
</template>
<script>
// import DrawService from '../service/draw-service'
import DataService from "../service/data-service";
import CommonTool from "../service/common";
import * as d3 from "d3";
export default {
  name: "problemStatistic",
  data() {
    return {
      svgid: "id_problem_chart",
      svgnormal: "id_normal",
      util: Object.getPrototypeOf(CommonTool)
    };
  },
  props: ["problemScore", "problemInfo", "studentInfo"],
  mounted() {
    // this.initialize()
    console.log(typeof(this.studentInfo))
    this.renderChart();
  },
  methods: {
    renderChart() {
      this.drawDotChart(this.transformByGradeDifficulty());
    },
    transformByGradeDifficulty() {
      // let data = this.problemScore
      let data = this.filterEqualGrade();
      let pinfo = this.problemInfo;
      // same difficulty, different grade
      for (let key in data) {
        data[key].level =
          (pinfo[key]["difficulty"] - 1) * 13 + pinfo[key]["grade"];
        data[key].difficulty = pinfo[key]["difficulty"];
        data[key].grade = pinfo[key]["grade"];
      }
      // same grade, different difficulty
      // for (let key in data) {
      //   data[key].level = pinfo[key]["grade"] * 5 + pinfo[key]["difficulty"];
      // }
      return data;
    },
    filterDifficulty(dval) {},
    filterEqualGrade() {
      let pscore = this.problemScore;
      let pinfo = this.problemInfo;
      let stuinfo = this.studentInfo;
      let data = {};
      for (let key in pscore) {
        data[key] = {
          seq: pscore[key]["seq"].filter((item, index) => {
            if (pscore[key]["user"][index] in stuinfo) {
              return (
                stuinfo[pscore[key]["user"][index]]["grade"] == pinfo[key]["grade"]
              );
            }
            return false;
          }),
          level:pscore[key]["level"]
        };
      }
      return data;
    },
    drawDotChart(data) {
      let width = 1000;
      let height = 500;
      let margin_left = 50;
      let margin_bottom = 50;
      let std = [];
      let quat = [];
      let diff = [];
      let avgscore = [];
      let difficulty = [];
      let keys = [];
      let grade = [];
      console.log(data)
      for (let key in data) {
        if(data[key]["seq"].length >0){
          quat.push(data[key]["seq"].length);
          avgscore.push(this.util._average(data[key]["seq"]));
          std.push(this.util._standardDev(data[key]["seq"]));
          diff.push(data[key]["level"]);
          difficulty.push(data[key]["difficulty"])
          keys.push(key)
          grade.push(data[key]["grade"])
        }
      }
      // [color, axisx, dot-size, axisy]
      let culsterdata = [std, diff, quat, avgscore, keys];
      // window.saveTextAsFile(JSON.stringify({
      //   "Std":std,
      //   "difficulty":difficulty,
      //   "avgscore":avgscore,
      //   "pid":keys,
      //   "grade":grade,
      // }), "data")
      let getcolor = d3
        .scaleLinear()
        .domain([Math.min(...culsterdata[0]), Math.max(...culsterdata[0])])
        .range(["green", "red"])
        .interpolate(d3.interpolateHcl);
      let xScale = d3
        .scaleLinear()
        .domain([0, Math.max(...culsterdata[1])])
        .range([0 + margin_left, width + margin_left]);
      let yScale = d3
        .scaleLinear()
        .domain([0, Math.max(...culsterdata[3])])
        .range([height, 0]);
      let rScale = d3
        .scaleLinear()
        .domain([Math.min(...culsterdata[2]), Math.max(...culsterdata[2])])
        .range([1, 10]);
      let svg = d3
        .select("#" + this.svgid)
        .attr("width", width + margin_left + 10)
        .attr("height", height + margin_bottom + 10);
      let xAxis = d3.axisBottom(xScale).ticks(5);
      let yAxis = d3.axisLeft(yScale).ticks(10);
      console.log(culsterdata)
      // "id, avg-score, diff, "
      svg
        .selectAll(".dot")
        .data(culsterdata[1])
        .enter()
        .append("circle")
        .attr("class", "dot")
        .attr("cx", function(d, i) {
          return xScale(d);
        })
        .attr("cy", function(d, i) {
          return yScale(culsterdata[3][i]) + 10;
        })
        .attr("r", (d, i) => rScale(culsterdata[2][i]))
        .attr("fill", function(d, i) {
          return getcolor(culsterdata[0][i]);
        })
        .attr("opacity", 0.3);
      svg
        .append("g")
        .attr("class", "x axis")
        .attr("transform", `translate(0, ${height + 10})`)
        .call(xAxis)
        .append("text")
        .attr("y", 15)
        .attr("transform", "translate(" + width + ",10)")
        .attr("fill", "#000")
        .text("Labeled difficulty level");
      svg
        .append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + margin_left + ",10)")
        .call(yAxis)
        .append("text")
        .attr("y", 15)
        .attr("transform", "translate(-50,10) rotate(-90)")
        .attr("fill", "#000")
        .text("Problem Avg-Score");
    },
  }
};
</script>
<style scoped>
</style>