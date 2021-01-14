<template>
    <div class="rightrange">
        <ejs-slider id='orientation' :value='value' :type="type" class="pa-0"></ejs-slider>
    </div>
</template>
<script>
import Vue from "vue";
import { SliderPlugin } from "@syncfusion/ej2-vue-inputs";
Vue.use(SliderPlugin);

export default {
  "name":"bottomRangeSlider",

  data() {
    return {
       value: [30, 70],
       type: 'Range',
    };
  },
  mounted() {
      
  },
  methods: {
  
  }
}
</script>
<style>
  @import "../../node_modules/@syncfusion/ej2-base/styles/material.css";
  @import "../../node_modules/@syncfusion/ej2-buttons/styles/material.css";
  @import "../../node_modules/@syncfusion/ej2-popups/styles/material.css";
  @import "../../node_modules/@syncfusion/ej2-vue-inputs/styles/material.css";
  .rightrange1500 {
    color: #008cff;
    height: 50px;
    width: 1000px;
  }
  .rightrange {
    color: #008cff;
    height: 50px;
    width: 1000px;
  }
  div {
  padding: 0 !important;
  }
</style>