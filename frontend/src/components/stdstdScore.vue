<template>
  <div>
    <div style="display: inline-flex;">
      <svg id="stdstd_chart"></svg>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import DrawService from '../service/draw-service'
import DataService from '../service/data-service'
export default {
  name: 'stdstdScore',
  components:{
  },
  props:["fullseq"],
  data () {
    return {
    }
  },
  mounted() {
    this.renderChart()
  },
  methods: {
    // refresh () {
        // let data = DataService.selectedUser
    //   Object.getPrototypeOf(DataService).getFullUserSequence.call(this, 'renderLineChart')
        // this.renderChart(data)
    // },
    renderChart(){
      let data = this.fullseq
      let config = {
        width: 500,
        height: 500,
        svgid: 'stdstd_chart'
      }
      // console.log(data.length)
      Object.getPrototypeOf(DrawService).drawStdScore(data, config)
      // Object.getPrototypeOf(DrawService).drawStepStd(data, config)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
