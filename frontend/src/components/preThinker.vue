<template>
  <div>
    <div style="display: inline-flex;">
      <svg id="idsvg"></svg>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import DrawService from '../service/draw-service';
import DataService from '../service/data-service';
import * as d3 from "d3";
export default {
  name: 'pointSequence',
  components:{
  },
  data () {
    return {
      width:1000,
      height:2000,
      margin_left: 50,
      margin_bottom:50,
      svgobj: null
    }
  },
  props:["exampleSeq", "studentInfo", "problemlist"],
  mounted() {
    this.refresh()
  },
  methods: {
    refresh () {
      this.svgobj = d3
        .select("#idsvg")
        .attr("width", this.width + this.margin_left)
        .attr("height", this.height + this.margin_bottom);
      this.renderLineChart()
      // this.renderProblem()
    },
    renderProblem(){
      let svg = d3.select("#idsvg")
      svg
      .append("g")
      .selectAll(".dot")
      .data(this.problemlist)
      .enter()
      .append("circle")
      .attr("r", 10)
      .attr("cx", (d,i) => 100)
      .attr("cy", (d, i) => 50 * (i+1))
      .attr("fill", "black")
    },
    renderPreThink(){
      let svg = d3.select("#idsvg")
      svg
      .append("g")
      .selectAll(".dot")
      .data(this.problemlist)
      .enter()
      .append("circle")
      .attr("r", 10)
      .attr("cx", (d,i) => 100)
      .attr("cy", (d, i) => 50 * (i+1))
      .attr("fill", "black")
    },
    getDensity(){
      
    },
    getThinkTime(data){
      return data.filter(item => item['thinkIndex']>0).map((userseq, uindex) => {
        // let maxtime = userseq[userseq.length-1][4]
        // let thinkIndex = userseq[0][1]
        // let userid = userseq[0][0]
        // let thinktime = userseq[thinkIndex][4]
        // let pscore = this.studentInfo[userid]["pscore"]
        // let score = 0;
        // if(pscore && uindex > 0){
        //   score = pscore[this.problemid]
        // }else{
        //   score = -1
        // }
        // let avgscore = this.studentInfo[userid]["avg"]
        // let std = this.studentInfo[userid]["std"]
        // return [userid, score, avgscore, thinktime, thinktime/(thinkIndex+1)]
        return [userseq["userid"], userseq['score'], userseq['score'], userseq["sequence"][userseq['thinkIndex']][4], userseq["sequence"][userseq['thinkIndex']][4]/(userseq['thinkIndex']+1)]
      }).filter(item => item[1] != undefined && item[2]!=undefined && item[3] != undefined)
    },
    renderLineChart(){
      let data = []
      let result = this.getThinkTime(this.exampleSeq)
      data.push(result.map(item => item[3]))
      data.push(result.map(item => item[2]))
      data.push(result.map(item => item[1]))
      data.push(result.map(item => item[4]))
      this.drawDotChart(data)
    },
    drawDotChart(data) {
      let svg = this.svgobj
      let width = 960;
      let height = 600;
      let margin_left = 50;
      let margin_bottom = 50;
      let xScale = d3
        .scaleLinear()
        .domain([Math.min(...data[0]), 100000])
        .range([margin_left, width]);
      let yScale = d3
        .scaleLinear()
        .domain([Math.min(...data[1]), Math.max(...data[1])])
        .range([height, 10]);
      let rScale = d3.scaleLinear()
        .domain([Math.min(...data[3]), 2382])
        .range([2,10]);
      
      let xAxis = d3.axisBottom(xScale).ticks(5);
      let yAxis = d3.axisLeft(yScale).ticks(10);
      svg.selectAll(".dot")
        .data(data[0])
        .enter()
        .append("circle")
        .attr("cx", function(d, i) {
          return xScale(data[0][i]);
        })
        .attr("cy", function(d, i) {
          return yScale(data[1][i]);
        })
        .attr("r", function(d,i){
          // return rScale(data[3][i])
          return 2
        })
        .attr("fill", function(d,i){
          if(data[2][i] == 0){
            return "red"
          }else if(data[2][i] == 100){
            return "green"
          }else{
            return "blue"
          }
        })
        .attr("opacity", 1);
      svg
        .append("g")
        .attr("class", "x axis")
        .attr("transform", `translate(0, ${height})`)
        .call(xAxis)
        .append("text")
        .attr("y", 15)
        .attr("transform", "translate(" + width + ",10)")
        .attr("fill", "#000")
        .text("Think time");
      svg
        .append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + margin_left + ",0)")
        .call(yAxis)
        .append("text")
        .attr("y", 15)
        .attr("transform", "translate(-50,10) rotate(-90)")
        .attr("fill", "#000")
        .text("Avg-Score");
    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
