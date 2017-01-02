<template lang="html">
    <div>
    <c-loading v-if="loading_status == 5"></c-loading>
    <c-error v-if="loading_status == 7"></c-error>
    <ul class="progress" v-if="loading_status == 6"><li id="progress-status">
            <div class="pg-title" style="color: #27b427;">运行状态</div>
            <div class="pg-main" v-if="work_status == 2" v-cloak>
                <svg id="svg-running" viewBox="-10 -10 220 220">
                    <path d="M 184 100 A 84 84 0 1 1 142 27.25386608210715" stroke-width="3" stroke="#27b427"></path>
                    <path d="M 60 90 L 100 135 L 200 20 " stroke-width="3" stroke="#27b427"></path>
                </svg>
            </div>
            <div class="pg-main" v-if="work_status == 0" v-cloak>
                <svg id="svg-halt" viewBox="-10 -10 220 220">
                    <path d="M 184 100 A 84 84 0 1 1 184 99" stroke-width="3" stroke="#27b427"></path>
                    <path d="M 50 100 L 150 100" stroke="#27b427" stroke-width="3"></path>
                </svg>
            </div>
            <div class="pg-main" v-if="work_status == 1" v-cloak>
                <svg id="stop" viewBox="-10 -10 220 220">
                    <circle r="85" cx="100" cy="100" stroke="#27b427" stroke-width="3"></circle>
                    <circle r="15" cx="50" cy="100" stroke="#27b427" stroke-width="3"></circle>
                    <circle r="15" cx="100" cy="100" stroke="#27b427" stroke-width="3"></circle>
                    <circle r="15" cx="150" cy="100" stroke="#27b427" stroke-width="3"></circle>
                </svg>

                <svg id="stop-rev" viewBox="-10 -10 220 220">
                    <circle r="85" cx="100" cy="100" stroke="#fff" stroke-width="6"></circle>
                    <circle r="15" cx="50" cy="100" stroke="#fff" stroke-width="6"></circle>
                    <circle r="15" cx="100" cy="100" stroke="#fff" stroke-width="6"></circle>
                    <circle r="15" cx="150" cy="100" stroke="#fff" stroke-width="6"></circle>
                </svg>
            </div>

            <div class="pg-info">
                <!-- status text-->
                <span v-if="work_status == 0">未 启 动</span>
                <span v-if="work_status == 1">启 动 中</span>
                <span v-if="work_status == 2">运 行 中</span>
            </div>

        </li><li id="progress-online-users">
            <div class="pg-title" style="color: blue;">在线用户</div>
            <div class="pg-main">
                <svg id="online-users-svg" viewBox="-10 -10 220 220">
                    <path :d="circle_paths[0]" stroke="blue" stroke-width="15" stroke-dashoffset="0"></path>
                </svg>

                <div id="online-num" class="central-number">{{ current_player }}</div>
                <div id="divider" class="central-number">／</div>
                <div id="total-num" class="central-number">{{ total_player }}</div>
            </div>

            <div class="pg-info">
                <span class="hint-text">在线人数： </span><span class="em_2_text">{{ current_player }}</span>
            </div>

            <div class="pg-info">
                <span class="hint-text">最大容量： </span><span class="em_2_text">{{ total_player }}</span>
            </div>
        </li><li id="progress-RAM-usage">
            <div class="pg-title" style="color: #ff4f38;">RAM 消耗</div>
            <div class="pg-main">
                <svg id="RAM-usage-svg" viewBox="-10 -10 220 220">
                    <path :d="circle_paths[1]" stroke="#ff4f38" stroke-width="15" stroke-dashoffset="0"></path>
                </svg>

                <div id="RAM-percent">{{ RAM_percent }}</div>
                <div id="RAM-percent-mark">%</div>
            </div>

            <div class="pg-info">
                <span class="hint-text">已用内存： </span><span>{{ current_RAM }}</span>&nbsp;<span>G</span>
            </div>

            <div class="pg-info">
                <span class="hint-text">最大内存： </span><span>{{ max_RAM }}</span>&nbsp;<span>G</span>
            </div>
        </li>
        <!--  Item  -->
    </ul>
    </div>
</template>

<script>
const LOADING = 5;
const LOAD_SUCCESS = 6;
const LOAD_ERROR = 7;
const HALT = 0;
const STARTING = 1;
const RUNNING = 2;

import Loading from "../../components/c-loading.vue";
import LoadingError from "../../components/c-error.vue";
import WebSocket from "../../lib/websocket";
import Vivus from 'vivus';

let ws = new WebSocket();
export default {
    components:{
        'c-loading' : Loading,
        'c-error': LoadingError
    },
    name: "server-status",
    data(){
        return {
            work_status: null,
            current_player: "--",
            total_player: "--",
            current_RAM: "--",
            max_RAM: "--",
            RAM_percent: "--",
            loading_status : LOADING,
            circle_paths:["", ""]
        }
    },
    methods:{
        // retrieve data from list
        // val = msg.val
        // $ref API
        init_status_list(val){
            console.log(val);
            this.loading_status = LOAD_SUCCESS;
            //$watch function will help us do some update work
            this.work_status = val.status;
            //update
            if(val.current_player != -1){
                let ratio = val.current_player / val.total_player;
                this.current_player = val.current_player;
                this._update_loop(0, ratio);
            }

            if(val.total_player != -1){
                this.total_player = val.total_player;
            }

            if(val.total_RAM != -1){
                this.max_RAM = (val.total_RAM / 1024);
            }

            if(val.RAM != -1){
                this.current_RAM = (val.RAM / 2014).toFixed(1);
                let ratio = val.RAM / val.total_RAM;
                this.RAM_percent = (ratio * 100).toFixed(0);
                this._update_loop(1, ratio);
            }
        },
        // set variables
        // $ref API
        set_status(status){
            if(status == STARTING || status == RUNNING){
                this.work_status = status;
            }else{
                this.work_status = HALT;
            }
        },

        // $ref API
        set_online_player(player){
            this.current_player = player;
            let _ratio = (player / this.total_player);
            this._update_loop(0, _ratio);
        },

        // $ ref API
        set_RAM(RAM){
            this.current_RAM = (RAM / 2014).toFixed(2);
            if(Number.isInteger(this.max_RAM)){
                let ratio = ((RAM / 1024) / this.max_RAM);
                this.RAM_percent = (ratio*100).toFixed(0);
                this._update_loop(1, ratio);
            }else{
                this._update_loop(1, 0);
            }
        },
        reset(){
            this.work_status = HALT;
            this.current_player = "-";
            this.current_RAM = "-";
            this.RAM_percent = "--";
            this._update_loop(0,0);
            this._update_loop(1,0);
        },
        // index = 0 ==> online players, index = 1 ==> RAM usages
        _update_loop(index, ratio){
            let polarToCartesian = (centerX, centerY, radius, angleInDegrees) => {
                var angleInRadians = (angleInDegrees-90) * Math.PI / 180.0;
                return {
                    x: centerX + (radius * Math.cos(angleInRadians)),
                    y: centerY + (radius * Math.sin(angleInRadians))
                };
            }

            let describeArc = (x, y, radius, startAngle, endAngle) => {
                var end = polarToCartesian(x, y, radius, endAngle);
                var start = polarToCartesian(x, y, radius, startAngle);
                var largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

                var d = [
                    "M", start.x, start.y,
                    "A", radius, radius, 0, largeArcFlag, 1, end.x, end.y
                ].join(" ");

                return d;
            }

            this.circle_paths[index] = describeArc(100, 100, 85, 0, 360 * ratio);
        },
        _UI_animation(work_status){
            let wa;
            let tr;
            function trig_rev() {
                setTimeout(function () {
                    tr.play();
                },400);
            }
            function trig_wait() {
                tr.reset();
                wa.reset();
                wa.play();
            }

            switch (work_status){
            case 0:
                new Vivus('svg-halt', {duration: 30 , type:"sync"});
                break;
            case 1:
                wa = new Vivus('stop', {duration: 30 , type:"sync", start:"manual"}, trig_rev);
                tr = new Vivus('stop-rev', {duration: 30 , type:"sync", start:"manual"}, trig_wait);
                trig_wait();
                break;
            case 2:
                new Vivus('svg-running', {duration: 30 , type:"sync"});
                break;
            }
        }
    },
    mounted(){
        this.$watch('work_status',(newVal, oldVal)=>{
            this.work_status = newVal;
            this._UI_animation(newVal);

            if(newVal == HALT){
                this.reset();
            }else if(newVal == RUNNING){
            }
        });
    }
}
</script>

<style>
 /*circle loop*/
@-webkit-keyframes load {
  0% {
    stroke-dashoffset: 0;
  }
}
@keyframes load {
  0% {
    stroke-dashoffset: 0;
  }
}
.progress {
    position: relative;
    display: inline-block;
    padding: 0;
    text-align: center;
    height: auto;
    width: 100%;
    background-color: transparent;
    margin-top: 10px;
    margin-bottom: 10px;
}
.progress > li {
    display: inline-block;
    position: relative;
    text-align: center;
    width:33.33%;
    height: 100%;
    vertical-align: top;
}
.progress .pg-main{
    width: 10rem;
    height: 10rem;
    margin-left: auto;
    margin-right: auto;
    position: relative;
    margin-top: 0.8rem;
    margin-bottom: 0.8rem;
}

.progress svg {
    width: 100%;
    height: 100%;
    fill:none;
}

div.central-number{
    font-size:18px;
    position: absolute;
    line-height: 25px;
    text-align: center;
}

span.em_2_text{
    width: 2em;
    display: inline-block;
}
/*online users*/
div#online-num{
    top:28px;
    left:20px;
    width:2em;
    color: blue;
}

div#divider{
    top:37px;
    left:37px;
    font-size: 25px;
}

div#total-num{
    top:50px;
    left:42px;
    width:2em;
    color: blue;
}

div.pg-info span.hint-text{
    color:gray;
    font-size: 13px;
}
div#RAM-percent{
    position: absolute;
    line-height: 25px;
    top:35px;
    left: 20px;
    text-align: center;
    font-size: 25px;
    width:2em;
    color: red;
}

div#RAM-percent-mark{
    position: absolute;
    line-height: 25px;
    top:42px;
    left:60px;
    font-size:13px;
    text-align: center;
}

div.pg-main #stop-rev{
    position: relative;
    top: -105px;
}
</style>
