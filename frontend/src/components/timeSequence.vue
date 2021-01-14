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
  name: 'timeSequence',
  components:{
  },
  data () {
    return {
    }
  },
  props:["exampleSeq", "problemid", "studentInfo"],
  mounted() {
    this.refresh()
  },
  methods: {
    refresh () {
      this.renderLineChart()
    },
    renderLineChart(){
      let data = this.exampleSeq;
      this.drawDotChart(data);
    },
    drawDotChart(data,configdata) {
      let width = 1000;
      let height = 4000;
      let margin_left = 50;
      let margin_bottom = 50;
      let xScale = d3
        .scaleLinear()
        .domain([0, 300000])
        .range([0, width]);
      let yScale = d3
        .scaleLinear()
        .domain([0, 200])
        .range([height, 0]);
      let getcolor = function(name){
        if(name == "mousemove")
          return "green"
        else if(name=="mousedown"){
          return "red"
        }
        return "black"
      }
      let svg = d3
        .select("#idsvg")
        .attr("width", width+margin_left)
        .attr("height", height+margin_bottom);
      let xAxis = d3.axisBottom(xScale).ticks(10);
      svg
        .append("g")
        .attr("class", "x axis")
        .attr("transform", `translate(50, 0)`)
        .call(xAxis)
      for(let i=0;i<data.length;i++){
          svg.append("text").attr("x", 0).attr("y", (i+1) * 4).attr("font-size", 5).text(data[i]["userid"] + " "+data[i]["score"])
          if(data[i]["score"] >= 75){
            svg.append("circle").attr("cx", 30).attr("cy", (i+1) * 4).attr("r", 3).attr("fill", "black")
          }else{
            svg.append("circle").attr("cx", 30).attr("cy", (i+1) * 4).attr("r", 3).attr("fill", "blue")
          }
          svg.append("g").selectAll(".cg").data(data[i]["sequence"]).enter()
          .append("circle")
          .attr("cx", (d, t) => xScale(d[4]) + 50)
          .attr("cy", (d, t) => (i + 1) * 4)
          .attr("r", (d, t) => {
            if(t == data[i]["thinkIndex"]){
              return 3
            }
            return 1
          })
          .attr("fill", (d, t) => getcolor(d[3]))
      }
    }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
