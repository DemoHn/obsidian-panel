<template lang="html">
    <div>
        <div class="ctrl-switch">
            <div style="margin-top:1.5rem;margin-bottom:1rem;"><b>控制掣</b></div>
                <button v-if="btn_status == 'pause'" class="btn btn-primary" :disabled="btn_disable" @click="stop_inst">停止</button>
                <button v-if="btn_status == 'start' || btn_status == 'starting'" class="btn btn-primary" :disabled="btn_disable" @click="start_inst">启动</button>
                <button v-if="btn_status == 'starting' || btn_status == 'pause'" class="btn btn-success" @click="terminate_inst">强行停止</button>
                <button v-if="btn_status == 'pause'" class="btn btn-danger" :disabled="btn_disable" @click="restart_inst">重新启动</button>

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

div.ctrl-switch{
    display: none;
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
