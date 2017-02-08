<template lang="html">
    <div>
        <div class="ctrl-switch">
            <div class="box box-default box-solid">
                <div class="box-header with-border">
                    <h3 class="box-title" style="font-size:16px;">控制掣</h3>
                </div>

                <div class="box-body no-padding" style="display:block">
                    <div class="box-btn-container" style="color: darkorange;" v-if="btn_status == 'pause'">
                        <button class="box-btn" :disabled="btn_disable" @click="stop_inst">
                            <i class="ion-ios-pause"></i><span class="gap">停止</span>
                        </button>
                    </div>

                    <div class="box-btn-container" style="color:#4c63e8;" v-if="btn_status == 'start' || btn_status == 'starting'">
                        <button class="box-btn" :disabled="btn_disable" @click="start_inst">
                            <i class="ion-ios-play"></i><span class="gap">启动</span>
                        </button>
                    </div>

                    <div class="box-btn-container" style="color: red;" v-if="btn_status == 'starting' || btn_status == 'pause'">
                        <button class="box-btn" @click="terminate_inst">
                            <i class="ion-close-round"></i><span class="gap">强行停止</span>
                        </button>
                    </div>

                    <div class="box-btn-container" style="color: green;"  v-if="btn_status == 'pause'">
                        <button class="box-btn" :disabled="btn_disable" @click="restart_inst">
                            <i class="ion-ios-loop-strong"></i><span class="gap">重新启动</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <!--this button will vanish on desktop but exist on mobile device and pad-->
        <button v-if="btn_status == 'start'" class="corner" :disabled="btn_disable" @click="start_inst" v-cloak>
            <i class="ion-ios-play" style="margin-left:4px;/*to make it more 'in center'*/"></i>

        </button>
        <button v-if="btn_status == 'pause'" class="corner" :disabled="btn_disable" @click="stop_inst" v-cloak>
            <i class="ion-ios-pause"></i>
        </button>
    </div>
</template>

<script>
    export default {
        name: 'ctrl-button',
        data(){
            return {
                "btn_status" : "start",
                "btn_disable": true
            }
        },methods:{
            //$ref API
            lock_button(){
                this.btn_disable = true;
            },

            unlock_button(){
                this.btn_disable = false;
            },

            init(work_status){
                if(work_status == 0){
                    this.unlock_button();
                    this.change_button_status("start");
                }else if(work_status == 1){
                    this.lock_button();
                    this.change_button_status("starting");
                }else if(work_status == 2){
                    this.unlock_button();
                    this.change_button_status("pause");
                }
            },
            // state = "start" | "pause"
            change_button_status(state){
                this.btn_status = state;
            },
            //emit methods
            start_inst(){
                this.$emit("start_inst");
            },
            stop_inst(){
                this.$emit("stop_inst");
            },
            restart_inst(){
                this.$emit("restart_inst");
            },
            terminate_inst(){
                this.$emit("terminate_inst");
            }
        }
    }
</script>

<style scoped>
button.corner{
    display: none;
}

span.gap{
    margin-left: 1rem;
}
div.box-btn-container{
    height: 3.8rem;
    width: 100%;
    border-bottom: 1px solid #dedede;
}

div.box-btn-container i{
    width: 1.25rem;
    display: inline-block;
    text-align: center;
}
button.box-btn{
    display: block;
    width: 100%;
    height:100%;
    border: none;
    outline: none;
    text-align:left;
    padding-left: 1.25rem;
    background: none;
    font-size: 1.5rem;
}

button.box-btn[disabled]{
    color: #bcbcbc;
}
div.ctrl-switch{
    display: none;
}

div.no-padding{
    padding: 0 !important;
}
@media(min-width: 1201px){
    div.ctrl-switch{
        display: block;
    }
}

@media (max-width: 1200px){
    button.corner{
        position: fixed;
        bottom:30px;
        right:20px;
        border:none;
        margin: 0;
        outline: none;
        display: block;
        width:60px;
        box-shadow:1px 1px 3px gray;
        height:60px;
        background-color: blueviolet;
        color: white;
        border-radius: 30px;
        line-height: 60px;
        text-align: center;
        z-index:200;
        font-size: 35px;
    }

    button.corner[disabled]{
        background-color: #be8aef; /*just change Lightness of `blueviolet`*/
    }
}
</style>
