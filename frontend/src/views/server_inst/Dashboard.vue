<template lang="html">
    <div>
        <div class="ctrl-bar">
            <inst-select ref="SelectF"></inst-select>
            <ctrl-button ref="CtrlF"></ctrl-button>
        </div>

        <div class="inst-content">
            <div class="row">
                <div class="col-md-7" id="dash_board">
                    <div class="box box-solid">
                        <div class="box-body">
                            <server-status ref="StatusF"></server-status>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import SelectInstance from "../../components/dashboard/inst-select.vue";
    import ControlButton from "../../components/dashboard/ctrl-button.vue";
    import ServerStatus from "../../components/dashboard/server-status.vue";
    import WebSocket from "../../lib/websocket";
    export default {
        components:{
            'inst-select' : SelectInstance,
            'ctrl-button' : ControlButton,
            'server-status' : ServerStatus
        },
        name: "Dashboard",
        data(){
            return {
                inst_id : null
            };
        },
        methods: {
            ws_init_status(){
                let ws = new WebSocket();
                let Status = this.$refs.StatusF;
                let Button = this.$refs.CtrlF;
                let x = 0;
                if(Number.isInteger(this.inst_id)){
                    let props = {
                        inst_id : this.inst_id
                    }
                    ws.send("process.get_instance_status", props, (msg)=>{
                        Status.init_status_list(msg.val);
                        Button.init(msg.val.status);
                    });
                }
            },
            aj_get_list(){
                let Select = this.$refs.SelectF;
                let ws = new WebSocket();
                ws.ajax("GET","/server_inst/api/get_inst_list", (msg)=>{
                    Select.init_inst_list(msg);
                    this.inst_id = msg.current_id;
                    this.ws_init_status();
                },(msg)=>{

                });
            }
        },
        mounted(){
            this.aj_get_list();
        }
    }
</script>

<style>
@media(min-width: 1201px){
    div.inst-content{
        position: relative;
        padding-left:250px;
        width:100%;
        z-index: 10;
        padding-top: 2rem;
    }

    div.ctrl-bar{
        width : 220px;
        position: relative;
        float: left;
        margin-top: 2rem;
        padding-left: 10px;
        padding-right: 10px;
        z-index: 12;
    }
}

@media(max-width: 767px){
    div.inst-content{
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 2rem;
    }
}
</style>
