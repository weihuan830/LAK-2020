import * as d3 from 'd3'
class Service {
    // eslint-disable-next-line no-useless-constructor
    constructor() {
        this.problemInfo = {}
        this.problemType = {}
        this.problemScore = {}
        this.studentInfo = {}
        this.exampleSeq = []
        this.linechartConfig = {
            width: 5000,
            height: 600,
            svgid: 'line_chart',
            span: 4,
            leftrange: [0, 100],
            bottomrange: [0, 500]
        }
        return this
    }
    getProblemInfo(callback) {
        let that = this;
        d3.json('http://localhost:8080/static/json/probleminfo.json').then(function(data) {
            DataService.problemInfo = data
            that[callback]()
        })
    }
    getProblemType(callback) {
        let that = this;
        d3.json('http://localhost:8080/static/json/problemtypes.json').then(function(data) {
            DataService.problemType = data
            that[callback]()
        })
    }
    getProblemScore(callback) {
        let that = this;
        d3.json('http://localhost:8080/static/json/problemscore.json').then(function(data) {
            DataService.problemScore = data
            that[callback]()
        })
    }
    getStudentInfo(callback) {
        let that = this;
        d3.json('http://localhost:8080/static/json/studentinfo.json').then(function(data) {
            DataService.studentInfo = data
            that[callback]()
        })
    }
    getExampleSeq(callback, name) {
        let that = this;
        d3.json('http://localhost:8080/static/json/sequences/' + name + '.json').then(function(data) {
            that[callback](name, data)
        })
    }
    getExampleSeq2(callback) {
        let that = this;
        d3.json('http://localhost:8080/static/json/example2.json').then(function(data) {
            DataService.exampleSeq2 = data
            that[callback]()
        })
    }
    getFullUserSequence(callback) {
        let that = this;
        let arr = ["pseqdiff", "fullseq", "seq_user_algebraic", "seq_user_data-handling", "seq_user_geometric", "seq_user_measures", "seq_user_numeric", "seq_user_spatial"]
        d3.json('http://localhost:8080/static/json/' + arr[1] + '.json').then(function(data) {
            if (callback) {
                DataService.fullseq = data
                that[callback](data)
            }
        })
    }
    getSequenceByTagName(callback) {
        let that = this;
        let arr = ["pseqdiff", "fullseq", "seq_user_algebraic", "seq_user_data-handling", "seq_user_geometric", "seq_user_measures", "seq_user_numeric", "seq_user_spatial"]
        d3.json('http://localhost:8080/static/json/' + arr[6] + '.json').then(function(data) {
            if (callback) {
                that[callback](data)
            }
        })
    }
}
const DataService = new Service()
export default DataService