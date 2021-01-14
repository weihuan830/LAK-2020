<template>
  <div>
    <div style="display: inline-flex;">
      <svg id="test_svg"></svg>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import DrawService from "../service/draw-service";
import DataService from "../service/data-service";
import * as d3 from "d3";
export default {
  name: "testView",
  components: {},
  props: ["problemlistData"],
  data() {
    return {
        statistic: []
    };
  },
  mounted() {
        this.renderDotChart()
  },
  methods: {

    
    renderDotChart() {
        for(let item in this.problemlistData){
            this.statistic = this.statistic.concat(this.getTimeScore(this.problemlistData[item]))
        }
        this.statistic.sort(function(a, b) {
            return a[0]-b[0];
        })
        this.statistic = this.statistic.slice(0, this.statistic.length-50)
        let minval = Math.min(...this.statistic.map(item => {
            return item[0]
        }))
        let maxval = Math.max(...this.statistic.map(item => {
            return item[0]
        }))
        let valscale = d3
            .scaleLinear()
            .domain([minval, 100000])
            .range([0, 20]);
        let cats = {}
        this.statistic.forEach(e => {
            let c = parseInt(valscale(e[0]));
            if ( cats[c] ) {
                if ( cats[c][e[2]] ) {
                    cats[c][e[2]]++;
                }else{
                    cats[c][e[2]] = 1;
                } 
            }else{
                cats[c] = { };
                cats[c][e[2]] = 1
            }
        });
        let people = {}
        this.statistic.forEach(e => {
            let c = parseInt(valscale(e[0]));
            if(people[e[3]]){
                people[e[3]].push([c, e[2]])
            }else{
                people[e[3]] = [[c, e[2]]]
            }
        });
        // const sumValues = obj => Object.values(obj).reduce((a, b) => a + b);
        // for(let key in cats){
        //     console.log(sumValues(cats[key]))
        // }
        console.log(cats)
        console.log(people)
        return cats
    },
    getTimeScore(data){
        return data.filter(item=>{
            return item["score"] >= 0 && item["thinkIndex"] >= 0;
        }).map(item => {
            let timeIndex = item["thinkIndex"];
            let timeSpan = item["sequence"][timeIndex][4] - item["sequence"][0][4]
            return [timeSpan, timeIndex, item["score"], item["userid"]]
        })
    },
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
