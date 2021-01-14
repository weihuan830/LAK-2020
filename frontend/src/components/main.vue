<template>
  <div>
    <div style="display: inline-flex;">
      <problemStatistic v-if="showproblemStatistic" :studentInfo="studentInfo" :problemInfo="problemInfo" :problemScore="problemScore"></problemStatistic>
    </div>
      <stdstdScore  v-if="showStd" :fullseq="fullseq"></stdstdScore>
      <testView v-if="showTestView" :problemlistData="problemlistData"></testView>
      <timeSequence v-if="showSequence" :studentInfo="studentInfo" :exampleSeq="exampleSeq2" :problemid="problemid"></timeSequence>
      <preThinker v-if="showPrethinker" :problemlist="problemlist" :problemid="problemid" :exampleSeq="exampleSeq" :studentInfo="studentInfo"></preThinker>
  </div>
</template>

<script>
import Vue from "vue";
// import DrawService from '../service/draw-service'
import DataService from '../service/data-service'
import problemStatistic from './problemStatistic'
import preThinker from './preThinker'
import timeSequence from './timeSequence'
import testView from './testView'
import stdstdScore from './stdstdScore'

export default {
  name: 'mainSequence',
  components:{
    problemStatistic,
    preThinker,
    timeSequence,
    testView,
    stdstdScore,
  },
  data () {
    return {
      problemlist: ["2841x00378c88165f5e16","3390x89c89efbd95796b2","3193xfa9eefc38d8ea289","3192x96c2dcdc94eac57b","20x746187641c59c168","2350x67dbe3cf12d34feb","3194xb3570a05e04eaa46","2344x8773a6898a1f33cf","2352x2c01d405736101be","2289x958b720e7416b65c","2343xccc49157c296ccd8","392xbf8da0c8c5262b4b","174x4dc558a71c4020b7","3331xde2f4ef708d49596","17x20d0226967291fe3","3260x04b8302ee2f3e356","3214xd1ecb03eaf4ed53a","2933x1aec2bd4ca7bf1ca","545x81d6ae36725e90e1","2957x081413147870fe2a","3560x3937fea475445c30","21x92b56cf7078123e4","680xf0cb97b391c7b6b8","3333xbe2b90abda67f262","3332xfbbe2cb982db7c99","611xca233ae480904689","95x565985f2824e4678","37x867ceefa9848cf63","38x51d27bb1a8e42c22","34x98b21dff3db8feb1","44x908f2a52efbba6ad","89x12193447d4ae80df","231x531ecdeeca9eff34","309x9d81d494e7d695e7"],
      // problemlist: ["20x746187641c59c168"],
      problemlistData:{},
      showproblemStatistic:false,
      showSequence: false,
      showTestView: false,
      showPrethinker:false,
      showStd:false,
      fullseq:null,
      problemid: "20x746187641c59c168",
      problemScore: null,
      problemInfo: null,
      selectedproblem:"",
      selectedpeople:"",
      readystate:0,
    }
  },
  mounted() {
    this.initialize()
  },
  methods: {
    initialize(){
      this.problemid = this.problemlist[4]
      Object.getPrototypeOf(DataService).getProblemInfo.call(this, 'ready')
      Object.getPrototypeOf(DataService).getProblemType.call(this, 'ready')
      Object.getPrototypeOf(DataService).getProblemScore.call(this, 'ready')
      Object.getPrototypeOf(DataService).getStudentInfo.call(this, 'ready')
      Object.getPrototypeOf(DataService).getFullUserSequence.call(this, 'ready')
      // for(var i=0;i<this.problemlist.length ;i++){
      //   Object.getPrototypeOf(DataService).getExampleSeq.call(this, 'sequenceGot', this.problemlist[i])
      // }
    },
    sequenceGot(name, data){
      this.problemlistData[name] = data;
      this.ready();
    },
    ready(){
      this.readystate +=1
      if(this.readystate >= (5)){
        this.problemScore = DataService.problemScore
        this.problemInfo = DataService.problemInfo
        this.problemType = DataService.problemType
        this.studentInfo = DataService.studentInfo
        this.fullseq = DataService.fullseq
        // this.exampleSeq = this.problemlistData["2841x00378c88165f5e16"]
        // this.showproblemStatistic = true
        // console.log(DataService)
        // this.showproblemStatistic = true
        // this.showSequence = true
        this.showStd = true
      }
    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
